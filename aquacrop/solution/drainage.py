import numpy as np

from numba import njit, f8, i8, b1
from numba.pycc import CC

try:
    from ..entities.soilProfile import SoilProfileNT_typ_sig
except:
    from entities.soilProfile import SoilProfileNT_typ_sig

# temporary name for compiled module
cc = CC("solution_drainage")


@cc.export("drainage", (SoilProfileNT_typ_sig, f8[:], f8[:]))
def drainage(prof, th_init, th_fc_Adj_init):
    """
    Function to redistribute stored soil water



    <a href="../pdfs/ac_ref_man_3.pdf#page=51" target="_blank">Reference Manual: drainage calculations</a> (pg. 42-65)


    *Arguments:*



    `prof`: `SoilProfile` : jit class object object containing soil paramaters

    `th_init`: `np.array` : initial water content

    `th_fc_Adj_init`: `np.array` : adjusted water content at field capacity


    *Returns:*


    `NewCond`: `InitialCondition` : InitCond object containing updated model paramaters

    `DeepPerc`:: `float` : Total Deep Percolation

    `FluxOut`:: `array-like` : water of water out of each compartment





    """

    # Store initial conditions in new structure for updating %%
    #     NewCond = InitCond

    #     th_init = InitCond.th
    #     th_fc_Adj_init = InitCond.th_fc_Adj

    #  Preallocate arrays %%
    thnew = np.zeros(th_init.shape[0])
    FluxOut = np.zeros(th_init.shape[0])

    # Initialise counters and states %%
    drainsum = 0

    # Calculate drainage and updated water contents %%
    for ii in range(th_init.shape[0]):
        # Specify layer for compartment
        cth_fc = prof.th_fc[ii]
        cth_s = prof.th_s[ii]
        ctau = prof.tau[ii]
        cdz = prof.dz[ii]
        cdzsum = prof.dzsum[ii]
        cKsat = prof.Ksat[ii]

        # Calculate drainage ability of compartment ii
        if th_init[ii] <= th_fc_Adj_init[ii]:
            dthdt = 0

        elif th_init[ii] >= cth_s:
            dthdt = ctau * (cth_s - cth_fc)

            if (th_init[ii] - dthdt) < th_fc_Adj_init[ii]:
                dthdt = th_init[ii] - th_fc_Adj_init[ii]

        else:
            dthdt = (
                ctau
                * (cth_s - cth_fc)
                * ((np.exp(th_init[ii] - cth_fc) - 1) / (np.exp(cth_s - cth_fc) - 1))
            )

            if (th_init[ii] - dthdt) < th_fc_Adj_init[ii]:
                dthdt = th_init[ii] - th_fc_Adj_init[ii]

        # Drainage from compartment ii (mm)
        draincomp = dthdt * cdz * 1000

        # Check drainage ability of compartment ii against cumulative drainage
        # from compartments above
        excess = 0
        prethick = cdzsum - cdz
        drainmax = dthdt * 1000 * prethick
        if drainsum <= drainmax:
            drainability = True
        else:
            drainability = False

        # Drain compartment ii
        if drainability == True:
            # No storage needed. Update water content in compartment ii
            thnew[ii] = th_init[ii] - dthdt

            # Update cumulative drainage (mm)
            drainsum = drainsum + draincomp

            # Restrict cumulative drainage to saturated hydraulic
            # conductivity and adjust excess drainage flow
            if drainsum > cKsat:
                excess = excess + drainsum - cKsat
                drainsum = cKsat

        elif drainability == False:
            # Storage is needed
            dthdt = drainsum / (1000 * prethick)

            # Calculate value of theta (thX) needed to provide a
            # drainage ability equal to cumulative drainage
            if dthdt <= 0:
                thX = th_fc_Adj_init[ii]
            elif ctau > 0:
                A = 1 + (
                    (dthdt * (np.exp(cth_s - cth_fc) - 1)) / (ctau * (cth_s - cth_fc))
                )
                thX = cth_fc + np.log(A)
                if thX < th_fc_Adj_init[ii]:
                    thX = th_fc_Adj_init[ii]

            else:
                thX = cth_s + 0.01

            # Check thX against hydraulic properties of current soil layer
            if thX <= cth_s:
                # Increase compartment ii water content with cumulative
                # drainage
                thnew[ii] = th_init[ii] + (drainsum / (1000 * cdz))
                # Check updated water content against thX
                if thnew[ii] > thX:
                    # Cumulative drainage is the drainage difference
                    # between theta_x and new theta plus drainage ability
                    # at theta_x.
                    drainsum = (thnew[ii] - thX) * 1000 * cdz
                    # Calculate drainage ability for thX
                    if thX <= th_fc_Adj_init[ii]:
                        dthdt = 0
                    elif thX >= cth_s:
                        dthdt = ctau * (cth_s - cth_fc)
                        if (thX - dthdt) < th_fc_Adj_init[ii]:
                            dthdt = thX - th_fc_Adj_init[ii]

                    else:
                        dthdt = (
                            ctau
                            * (cth_s - cth_fc)
                            * (
                                (np.exp(thX - cth_fc) - 1)
                                / (np.exp(cth_s - cth_fc) - 1)
                            )
                        )

                        if (thX - dthdt) < th_fc_Adj_init[ii]:
                            dthdt = thX - th_fc_Adj_init[ii]

                    # Update drainage total
                    drainsum = drainsum + (dthdt * 1000 * cdz)
                    # Restrict cumulative drainage to saturated hydraulic
                    # conductivity and adjust excess drainage flow
                    if drainsum > cKsat:
                        excess = excess + drainsum - cKsat
                        drainsum = cKsat

                    # Update water content
                    thnew[ii] = thX - dthdt

                elif thnew[ii] > th_fc_Adj_init[ii]:
                    # Calculate drainage ability for updated water content
                    if thnew[ii] <= th_fc_Adj_init[ii]:
                        dthdt = 0
                    elif thnew[ii] >= cth_s:
                        dthdt = ctau * (cth_s - cth_fc)
                        if (thnew[ii] - dthdt) < th_fc_Adj_init[ii]:
                            dthdt = thnew[ii] - th_fc_Adj_init[ii]

                    else:
                        dthdt = (
                            ctau
                            * (cth_s - cth_fc)
                            * (
                                (np.exp(thnew[ii] - cth_fc) - 1)
                                / (np.exp(cth_s - cth_fc) - 1)
                            )
                        )
                        if (thnew[ii] - dthdt) < th_fc_Adj_init[ii]:
                            dthdt = thnew[ii] - th_fc_Adj_init[ii]

                    # Update water content in compartment ii
                    thnew[ii] = thnew[ii] - dthdt
                    # Update cumulative drainage
                    drainsum = dthdt * 1000 * cdz
                    # Restrict cumulative drainage to saturated hydraulic
                    # conductivity and adjust excess drainage flow
                    if drainsum > cKsat:
                        excess = excess + drainsum - cKsat
                        drainsum = cKsat

                else:
                    # Drainage and cumulative drainage are zero as water
                    # content has not risen above field capacity in
                    # compartment ii.
                    drainsum = 0

            elif thX > cth_s:
                # Increase water content in compartment ii with cumulative
                # drainage from above
                thnew[ii] = th_init[ii] + (drainsum / (1000 * cdz))
                # Check new water content against hydraulic properties of soil
                # layer
                if thnew[ii] <= cth_s:
                    if thnew[ii] > th_fc_Adj_init[ii]:
                        # Calculate new drainage ability
                        if thnew[ii] <= th_fc_Adj_init[ii]:
                            dthdt = 0
                        elif thnew[ii] >= cth_s:
                            dthdt = ctau * (cth_s - cth_fc)
                            if (thnew[ii] - dthdt) < th_fc_Adj_init[ii]:
                                dthdt = thnew[ii] - th_fc_Adj_init[ii]

                        else:
                            dthdt = (
                                ctau
                                * (cth_s - cth_fc)
                                * (
                                    (np.exp(thnew[ii] - cth_fc) - 1)
                                    / (np.exp(cth_s - cth_fc) - 1)
                                )
                            )
                            if (thnew[ii] - dthdt) < th_fc_Adj_init[ii]:
                                dthdt = thnew[ii] - th_fc_Adj_init[ii]

                        # Update water content in compartment ii
                        thnew[ii] = thnew[ii] - dthdt
                        # Update cumulative drainage
                        drainsum = dthdt * 1000 * cdz
                        # Restrict cumulative drainage to saturated hydraulic
                        # conductivity and adjust excess drainage flow
                        if drainsum > cKsat:
                            excess = excess + drainsum - cKsat
                            drainsum = cKsat

                    else:
                        drainsum = 0

                elif thnew[ii] > cth_s:
                    # Calculate excess drainage above saturation
                    excess = (thnew[ii] - cth_s) * 1000 * cdz
                    # Calculate drainage ability for updated water content
                    if thnew[ii] <= th_fc_Adj_init[ii]:
                        dthdt = 0
                    elif thnew[ii] >= cth_s:
                        dthdt = ctau * (cth_s - cth_fc)
                        if (thnew[ii] - dthdt) < th_fc_Adj_init[ii]:
                            dthdt = thnew[ii] - th_fc_Adj_init[ii]

                    else:
                        dthdt = (
                            ctau
                            * (cth_s - cth_fc)
                            * (
                                (np.exp(thnew[ii] - cth_fc) - 1)
                                / (np.exp(cth_s - cth_fc) - 1)
                            )
                        )
                        if (thnew[ii] - dthdt) < th_fc_Adj_init[ii]:
                            dthdt = thnew[ii] - th_fc_Adj_init[ii]

                    # Update water content in compartment ii
                    thnew[ii] = cth_s - dthdt

                    # Update drainage from compartment ii
                    draincomp = dthdt * 1000 * cdz
                    # Update maximum drainage
                    drainmax = dthdt * 1000 * prethick

                    # Update excess drainage
                    if drainmax > excess:
                        drainmax = excess

                    excess = excess - drainmax
                    # Update drainsum and restrict to saturated hydraulic
                    # conductivity of soil layer
                    drainsum = draincomp + drainmax
                    if drainsum > cKsat:
                        excess = excess + drainsum - cKsat
                        drainsum = cKsat

        # Store output flux from compartment ii
        FluxOut[ii] = drainsum

        # Redistribute excess in compartment above
        if excess > 0:
            precomp = ii + 1
            while (excess > 0) and (precomp != 0):
                # Update compartment counter
                precomp = precomp - 1
                # Update layer counter
                # precompdf = Soil.Profile.Comp[precomp]

                # Update flux from compartment
                if precomp < ii:
                    FluxOut[precomp] = FluxOut[precomp] - excess

                # Increase water content to store excess
                thnew[precomp] = thnew[precomp] + (excess / (1000 * prof.dz[precomp]))

                # Limit water content to saturation and adjust excess counter
                if thnew[precomp] > prof.th_s[precomp]:
                    excess = (
                        (thnew[precomp] - prof.th_s[precomp]) * 1000 * prof.dz[precomp]
                    )
                    thnew[precomp] = prof.th_s[precomp]
                else:
                    excess = 0

    ## Update conditions and outputs ##
    # Total deep percolation (mm)
    DeepPerc = drainsum
    # Water contents
    # NewCond.th = thnew

    return thnew, DeepPerc, FluxOut


if __name__ == "__main__":
    cc.compile()

def test_compile_time():
    import time

    start = time.time()
    import aquacrop  # tests compile time

    end = time.time()
    t = end - start
    print(t)
    assert t < 60

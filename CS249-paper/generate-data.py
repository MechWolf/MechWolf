import mechwolf as mw

# create the components
pump = mw.DummyPump(name="Dummy pump")
tube = mw.Tube("1 foot", "1/16 in", "2/16 in", "PVC")

for failure_type in ["slow down"]:
    for invocation_threshold in range(820, 900, 20):
        print(failure_type, invocation_threshold)

        sensors = [
            mw.ErraticDummySensor(
                failure_type,
                name="Sensor " + str(i),
                invocation_threshold=invocation_threshold,
            )
            for i in range(200)
        ]

        # create apparatus
        A = mw.Apparatus()
        for sensor in sensors:
            A.add(pump, sensor, tube)

        P = mw.Protocol(A)
        for sensor in sensors:
            P.add(
                sensor,
                rate="50 Hz",
                start="0 secs",
                stop=f"{int(invocation_threshold / 10) + 5} secs",
            )

        # Returns immediately with an Experiment object that will update as it gets new data
        E = P.execute(
            confirm=True,
            log_file_verbosity="warning",
            log_file=False,
            data_file=f"./data/{failure_type.replace(' ', '_')}-{invocation_threshold}.data.jsonl",
        )

export default (protocol) => {
  // Generates a Google timeline chart from mechwolf.Protocol in json format.
  const columns = [
    { type: "string", id: "Device" },
    { type: "string", id: "Setting"}
    { type: "date", id: "Time" },
  ];



  return (
    <Chart
            chartType="Timeline"
            data={[columns, ...rows]}
            width="100%"
            height="400px"
    />
  );
}

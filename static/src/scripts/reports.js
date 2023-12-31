var chartData1 = [];

function generateChartData() {
    var firstDate = new Date();
    firstDate.setDate(firstDate.getDate() - 500);
    firstDate.setHours(0, 0, 0, 0);

    for (var i = 0; i < 500; i++) {
        var newDate = new Date(firstDate);
        newDate.setDate(newDate.getDate() + i);

        var a1 = Math.round(Math.random() * (40 + i)) + 100 + i;
        var b1 = Math.round(Math.random() * (1000 + i)) + 500 + i * 2;

        chartData1.push({
            date: newDate,
            value: a1,
            volume: b1
        });
    }
    console.log(chartData1)
}

AmCharts.ready(function() {
    generateChartData();
    createStockChart();
});

function createStockChart() {
    var chart = new AmCharts.AmStockChart();
    chart.pathToImages = "http://www.amcharts.com/lib/images/";

    // DATASETS //////////////////////////////////////////
    // create data sets first
    var dataSet1 = new AmCharts.DataSet();
    dataSet1.title = "first data set";
    dataSet1.fieldMappings = [{
        fromField: "value",
        toField: "value"},
    {
        fromField: "volume",
        toField: "volume"}];
    dataSet1.dataProvider = chartData1;
    dataSet1.categoryField = "date";

   
    // set data sets to the chart
    chart.dataSets = [dataSet1];

    // PANELS ///////////////////////////////////////////                                                  
    // first stock panel
    var stockPanel1 = new AmCharts.StockPanel();
    stockPanel1.showCategoryAxis = false;
    stockPanel1.title = "Value";
    stockPanel1.percentHeight = 60;
    
    // add value axes
    var valueAxis1 = new AmCharts.ValueAxis();
    stockPanel1.addValueAxis(valueAxis1);
    
    var valueAxis2 = new AmCharts.ValueAxis();
    valueAxis2.position = "right";
    stockPanel1.addValueAxis(valueAxis2);

    // graph of first stock panel
    var graph1 = new AmCharts.StockGraph();
    graph1.title = "Temperature";
    graph1.valueField = "value";
    graph1.lineThickness = 3;
    graph1.lineColor = "#00cc00";
    graph1.useDataSetColors = false;
    stockPanel1.addStockGraph(graph1);

    // create stock legend                
    stockPanel1.stockLegend = new AmCharts.StockLegend();
    var graph1 = new AmCharts.StockGraph();
    graph1.title = "Humidity";
    graph1.valueField = "value";
    graph1.lineThickness = 3;
    graph1.lineColor = "#900cdc";
    graph1.useDataSetColors = false;
    stockPanel1.addStockGraph(graph1);

    // create stock legend                
    stockPanel1.stockLegend = new AmCharts.StockLegend();

    var graph2 = new AmCharts.StockGraph();
    graph2.title = "Shake";
    graph2.valueField = "volume";
    graph2.type = "column";
    graph2.showBalloon = false;
    graph2.fillAlphas = 0.5;
    graph2.valueAxis = valueAxis2;
    stockPanel1.addStockGraph(graph2);

    // set panels to the chart
    chart.panels = [stockPanel1];


    // OTHER SETTINGS ////////////////////////////////////
    var sbsettings = new AmCharts.ChartScrollbarSettings();
    sbsettings.graph = graph1;
    sbsettings.usePeriod = "WW";
    chart.chartScrollbarSettings = sbsettings;


    // PERIOD SELECTOR ///////////////////////////////////
    var periodSelector = new AmCharts.PeriodSelector();
    periodSelector.position = "bottom";
    periodSelector.periods = [{
        period: "DD",
        count: 10,
        label: "10 days"},
    {
        period: "MM",
        selected: true,
        count: 1,
        label: "1 month"},
    {
        period: "YYYY",
        count: 1,
        label: "1 year"},
    {
        period: "YTD",
        label: "YTD"},
    {
        period: "MAX",
        label: "MAX"}];
    chart.periodSelector = periodSelector;


    chart.write('chartdiv');
}
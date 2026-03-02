// ******* DATA LOADING *******
async function loadData() {
    // map data source
    // https://github.com/topojson/us-atlas?tab=readme-ov-file
    // Using locally processed data from automated pipeline
    const beeData = await d3.csv('data/processed/bee_data.csv');

    // All data processing is now done in the backend pipeline
    // CSV columns are already properly formatted with underscores
    const mapData = await d3.json('js/data/us-states.json');

    return { beeData, mapData };
}


// ******* STATE MANAGEMENT *******
// communicate across the visualizations
const globalApplicationState = {
    //init to these 3 states to show state sekction tool
    selectedLocations: ["California", "Texas", "Michigan"],

    beeData: null,
    mapData: null,

    usMap: null,
    lineChart: null,

    // these are heights minus paddings
    svgWidth: null,
    svgHeight: null,
    gradientWidth: null,
    padding: null,

    yData: "Starting_Colonies"
};

//******* SET UP FITTED HTML ITEMS *******
addFittedSVGs();


//******* APPLICATION MOUNTING *******
loadData().then((loadedData) => {

    // Store the loaded data into the globalApplicationState
    globalApplicationState.beeData = loadedData.beeData;
    globalApplicationState.mapData = loadedData.mapData;

    //-----------------------
    // make all data numerical

    // columns to not convert to numeric
    const excludedColumns = ['date', 'State'];
    const columnNames = Object.keys(globalApplicationState.beeData[0]);

    // convert all other columns to numeric
    globalApplicationState.beeData.forEach(d => {
        columnNames.forEach(col => {
            // check if the column is not in the excluded list
            if (!excludedColumns.includes(col) && d[col]) {
                d[col] = +d[col]; // convert to numeric
            }
        });
    });

    console.log(globalApplicationState.beeData)
    console.log(globalApplicationState.mapData)

    //----------------------------
    //vis setup

    // init line chart and add it to global state 
    const lineChart = new LineChart(globalApplicationState);
    globalApplicationState.lineChart = lineChart;


    // init map and add it to global state 
    const usMap = new MapVis(globalApplicationState);
    globalApplicationState.usMap = usMap;

    // add a click listener to clear button
    d3.select("#clear-button").on("click", function (event) {
        globalApplicationState.selectedLocations = [];
        usMap.drawMap();
    });
});

function addFittedSVGs() {
    // ── size math ─────────────────────────────────────────────
    const MAP_WIDTH_TO_HEIGHT_RATIO = 1.75;
    const GRADIENT_WIDTH_RATIO      = 0.1;
    const PADDING_PERCENT           = 0.07;

    const screenWidth = window.innerWidth;

    globalApplicationState.padding       = Math.floor((screenWidth / 2) * PADDING_PERCENT);
    globalApplicationState.svgWidth      = Math.floor(screenWidth / 2 - globalApplicationState.padding * 2);
    globalApplicationState.svgHeight     = Math.floor(globalApplicationState.svgWidth / MAP_WIDTH_TO_HEIGHT_RATIO);
    globalApplicationState.gradientWidth = Math.floor(globalApplicationState.svgWidth * GRADIENT_WIDTH_RATIO);

    const svgW  = globalApplicationState.svgWidth  + globalApplicationState.padding * 2;
    const svgH  = globalApplicationState.svgHeight + globalApplicationState.padding * 2 + globalApplicationState.padding;

    const contentDiv = d3.select("#content");

    // ── Map column ────────────────────────────────────────────
    const mapCol = contentDiv.append("div").attr("class", "viz-col");

    mapCol.append("div")
        .attr("class", "viz-col__title")
        .text("National Average by State");

    const mapSVG = mapCol.append("svg")
        .attr("id", "map")
        .attr("width", svgW)
        .attr("height", svgH);

    mapSVG.append("g").attr("id", "country-outline");
    mapSVG.append("g").attr("id", "states");
    mapSVG.append("g").attr("id", "legend");

    // ── Line-chart column ─────────────────────────────────────
    const chartCol = contentDiv.append("div").attr("class", "viz-col");

    chartCol.append("div")
        .attr("class", "viz-col__title")
        .append("span")
        .attr("id", "line-title-text")
        .text("State Data Over Time");

    const lineChartSVG = chartCol.append("svg")
        .attr("id", "line-chart")
        .attr("width", svgW + 10)
        .attr("height", svgH);

    lineChartSVG.append("g").attr("id", "x-axis");
    lineChartSVG.append("g").attr("id", "y-axis");
    lineChartSVG.append("g").attr("id", "lines");
    lineChartSVG.append("g").attr("id", "overlay").append("line");

    // ── init controls ─────────────────────────────────────────
    addDropDownBox();
}

function addDropDownBox() {
    // data to bind to drop down selection
    const dataMaping = {
        Starting_Colonies: 'Starting Colonies',
        Diseases: 'Colonies Affected By Diseases %',
        Pesticides: 'Colonies Affected By Pesticides %',
        //Other: 'Other %',
        //Unknown: 'Unknown %',
        Varroa_mites: 'Colonies Affected By Varroa Mites %',
        Other_pests_and_parasites: 'Affected By Other Pests and Parasites %',
        Max_Colonies: 'Max Colonies',
        Lost_colonies: 'Lost Colonies',
        Percent_Lost: 'Lost Colonies %',
        Added_colonies: 'Added Colonies',
        //Renovated_colonies: 'Renovated Colonies',
        //Percent_renovated: 'Percent Renovated %'
    }

    // hydrate existing drop down in the control bar
    const dropDown = d3.select("#data-select")
        .on("change", () => {
            const value = dropDown.property("value");
            globalApplicationState.yData = value;
            globalApplicationState.usMap.updateDataType();
            d3.select("#line-title-text").text(dataMaping[value]);
        });

    dropDown.selectAll("option").remove();

    // bind data and set value and text functions
    var options = dropDown.selectAll("myOptions")
        .data(Object.keys(dataMaping))
        .enter()
        .append("option")
        // set up option text
        // text is the value of dataMaping
        .text(function (d) {
        return dataMaping[d];
        })
        // set up select box value to be the key of dataMaping
        .attr("value", function (d) {
            return d;
        });

    dropDown.property("value", globalApplicationState.yData);
    globalApplicationState.yData = dropDown.property("value");
    d3.select("#line-title-text").text(dataMaping[globalApplicationState.yData]);

}

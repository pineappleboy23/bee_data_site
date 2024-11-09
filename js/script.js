// ******* DATA LOADING *******
async function loadData() {
    // map data source
    // https://github.com/topojson/us-atlas?tab=readme-ov-file
    const beeData = await d3.csv('https://raw.githubusercontent.com/pineappleboy23/DS_data/refs/heads/main/merged_df.csv');

    // names of column to delete
    const unneededColumns = ["table_x", "table_y", "Month"];

    // Date column to date
    beeData.forEach(d => {
        if (d["Date"]) {
            d.date = d["Date"];
            delete d["Date"];
        }
        // replace spaces with underscores
        for (let key in d) {
            const newKey = key.replace(/ /g, "_"); // replace spaces with underscores
            if (newKey !== key) {
                d[newKey] = d[key];
                delete d[key];
            }

            // remove unwanted columns
            if (unneededColumns.includes(newKey)) {
                delete d[newKey];
            }
        }
    });

    console.log(Object.keys(beeData[0]))
    console.log(1)

    const mapData = await d3.json('js/data/us-states.json');

    return { beeData, mapData };
}


// ******* STATE MANAGEMENT *******
// communicate across the visualizations
const globalApplicationState = {
    selectedLocations: [],

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
    //--------------------------
    // do screen size math
    const MAP_WIDTH_TO_HEIGHT_RATIO = 1.75;
    const GRADIENT_WIDTH_RATIO = .1;
    const PADDING_PERCENT = .07; //percent of screen space on top and bottom and 2x on the left

    // get screen width
    let screenWidth = window.innerWidth * .9;

    // make each piece proportionally sized
    //                                PADDING_PERCENT of one display
    globalApplicationState.padding = Math.floor((screenWidth / 2) * PADDING_PERCENT);
    // half of width minus padding
    globalApplicationState.svgWidth = Math.floor(screenWidth / 2 - globalApplicationState.padding * 2);

    // width divided by ratio
    globalApplicationState.svgHeight = Math.floor(globalApplicationState.svgWidth / MAP_WIDTH_TO_HEIGHT_RATIO);
    // width * gradient ratio
    globalApplicationState.gradientWidth = Math.floor(globalApplicationState.svgWidth * GRADIENT_WIDTH_RATIO);

    //---------------------------------
    //add html content

    const width = globalApplicationState.svgWidth + globalApplicationState.padding * 2;
    const height = globalApplicationState.svgHeight + globalApplicationState.padding * 2;

    // Select the content div
    const contentDiv = d3.select("#content");

    // Append the map SVG element
    const mapSVG = contentDiv.append("svg")
        .attr("id", "map")
        .attr("width", width)
        .attr("height", height);

    // Add g elements inside map SVG
    mapSVG.append("g").attr("id", "country-outline");
    mapSVG.append("g").attr("id", "states");

    // Append the line-chart SVG element
    const lineChartSVG = contentDiv.append("svg")
        .attr("id", "line-chart")
        .attr("width", width + 10)
        .attr("height", height);

    // Add g elements inside line-chart SVG
    lineChartSVG.append("g").attr("id", "x-axis");
    lineChartSVG.append("g").attr("id", "y-axis");
    lineChartSVG.append("g").attr("id", "lines");

    // Add the overlay group with a line inside
    lineChartSVG.append("g")
        .attr("id", "overlay")
        .append("line");

    // new line for selectors
    contentDiv.append("br");

    // Append the button at the end of the content div
    contentDiv.append("button")
        .attr("id", "clear-button")
        .text("Clear Selected States");
}
$(document).ready(function() {
    $('#weather').DataTable( {
        data: dataSet,
        columns: [
            { title: "Date" },
            { title: "temperature" },
            { title: "humidity" },
            { title: "pollen" },
            { title: "air_quality" },
            { title: "so" },
            { title: "no" }       
              
        ]
    } );
} );

var dataSet = [
    [
      
      "21-10-2014",
       "34",
       "76%",
        "Good",
        "Bad",
		"Very Good",
		"Low"
    ],
    [
      
        "25-10-2004",
         "43",
         "76%",
          "Good",
          "Bad",
          " Bad",
          "High"
      ],
      [
      
        "21-10-2018",
         "34",
         "76%",
          "Good",
          "Bad",
          " Bad",
          "Low"
      ],
      [
      
        "21-10-2002",
         "34",
         "76%",
          "Good",
          "Bad",
          "Very Good",
          "Low"
      ],
      [
      
        "21-6-2003",
         "34",
         "76%",
          "Good",
          "Bad",
          "Very Bad",
          "Low"
      ],
      [
      
        "21-10-2004",
         "34",
         "76%",
          "Good",
          "Bad",
          "Very Bad",
          "Low"
      ],
];

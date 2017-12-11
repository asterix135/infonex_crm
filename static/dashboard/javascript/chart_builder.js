const topLabels = [
  'Govt',
  'Indigenous',
  'Private'
];
const labels = [
  'Federal Govt',
  'Provincial Govt',
  'MUSH',
  'Indigenous',
  'Private Sector',
  'Other'
];
const pieOptions = {
  labelInterpolationFnc: function(value) {
    return value[0]
  }
};

const pieResponsiveOptions = [
  ['screen and (min-width: 640px)', {
    chartPadding: 30,
    labelOffset: 100,
    labelDirection: 'explode',
    labelInterpolationFnc: function(value) {
      return value;
    }
  }],
  ['screen and (min-width: 1024px)', {
    labelOffset: 80,
    chartPadding: 20
  }]
];
const topData2017 = {
  labels: topLabels,
  series: [
    944410.85,
    228009.3,
    523133.3
  ]
};
const topData2016 = {
  labels: topLabels,
  series: [
    725153.3,
    198688,
    437800
  ]
};
const topData2015 = {
  labels: topLabels,
  series: [
    689070.6,
    209186.8,
    718728.65
  ]
}
var data2017 = {
  // A labels array that can contain any sort of values
  labels: labels,
  // Our series array that contains series objects or in this case series data arrays
  series: [
    518810.35,
    324310.5,
    101290,
    228009.3,
    409619.3,
    113514
  ]
};
var data2016 = {
  labels: labels,
  series: [
    509928.6,
    156128.7,
    59066,
    198699,
    341260.5,
    96593.5
  ]
};
var data2015 = {
  labels: labels,
  series: [
    374779,
    241456.5,
    72835.1,
    209186.8,
    540598.86,
    178129.78
  ]
};
const sales2017 = {
  labels: labels,
  series: [
    293836.35,
    154906.5,
    37429,
    148252.3,
    235814.3,
    50447
  ]
};
const mktg2017 = {
  labels: labels,
  series: [
    224974,
    169404,
    63861,
    79757,
    173805,
    47976
  ]
};
const sales2016 = {
  labels: labels,
  series: [
    329488.1,
    94364.2,
    22386,
    166916,
    214886.5,
    61059
  ]
};
const mktg2016 = {
  labels: labels,
  series: [
    180470.5,
    61764.5,
    36680,
    31783,
    126374,
    30383.5
  ]
};


new Chartist.Pie('#top-2017', topData2017);
new Chartist.Pie('#top-2016', topData2016);
new Chartist.Pie('#top-2015', topData2015);


new Chartist.Pie('#revenue-2017', data2017);
new Chartist.Pie('#revenue-2016', data2016);
new Chartist.Pie('#revenue-2015', data2015);

new Chartist.Pie('#marketing-2016', mktg2016);
new Chartist.Pie('#sales-2016', sales2016);

new Chartist.Pie('#marketing-2017', mktg2017);
new Chartist.Pie('#sales-2017', sales2017);

const barOptions = {
  seriesBarDistance: 10
};

const barResponsiveOptions = [
  ['screen and (max-width: 640px)', {
    seriesBarDistance: 5,
    axisX: {
      labelInterpolationFnc: function (value) {
        return value[0];
      }
    }
  }]
];

const topBarData = {
  labels: topLabels,
  series:[
    [689070.6, 209186.8, 718728.65],
    [725153.3, 198688, 437800],
    [944410.85, 228009.3, 523133.3]
  ]
};
const detailBarData = {
  labels: labels,
  series: [
    [374779, 241456.5, 72835.1, 209186.8, 540598.86, 178129.78],
    [509928.6, 156128.7, 59066, 198699, 341260.5, 96593.5],
    [518810.35, 324310.5, 101290, 228009.3, 409619.3, 113514]
  ]
};

new Chartist.Bar('#top-bar', topBarData, barOptions, barResponsiveOptions);
new Chartist.Bar('#detail-bar', detailBarData, barOptions, barResponsiveOptions);

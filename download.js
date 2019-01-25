var data = source.data;
var filetext = 'SEQN,RAW_CURVE,FVC_MAX,FEV1,FEV3,FEV6,PEAK_EXPIRATORY,MAX_MID_EXPIRATORY,PSEUDO_PSU,AGE,GENDER2,GENDER,HEIGHT,WEIGHT,BMI,SESSION_BEST,SESSION_MEAN,SESSION_STD,SESSION_MEDIAN,SESSION_IQR,SESSION_MINIMUM,SESSION_MAXIMUM,SESSION_MAX_DISTANCE,SESSION_MEDIAN_DISTANCE\n';
for (var i = 0; i < data['SEQN'].length; i++) {
    var currRow = [data['SEQN'][i].toString(),
                   data['RAW_CURVE'][i].toString(),
                   data['FVC_MAX'][i].toString(),
                   data['FEV1'][i].toString(),
                   data['FEV3'][i].toString(),
                   data['FEV6'][i].toString(),
                   data['PEAK_EXPIRATORY'][i].toString(),
                   data['MAX_MID_EXPIRATORY'][i].toString(),
                   data['PSEUDO_PSU'][i].toString(),
                   data['AGE'][i].toString(),
                   data['GENDER2'][i].toString(),
                   data['GENDER'][i].toString(),
                   data['HEIGHT'][i].toString(),
                   data['WEIGHT'][i].toString(),
                   data['BMI'][i].toString(),
                   data['SESSION_BEST'][i].toString(),
                   data['SESSION_MEAN'][i].toString(),
                   data['SESSION_STD'][i].toString(),
                   data['SESSION_MEDIAN'][i].toString(),
                   data['SESSION_IQR'][i].toString(),
                   data['SESSION_MINIMUM'][i].toString(),
                   data['SESSION_MAXIMUM'][i].toString(),
                   data['SESSION_MAX_DISTANCE'][i].toString(),
                   data['SESSION_MEDIAN_DISTANCE'][i].toString().concat('\n')];

    var joined = currRow.join();
    filetext = filetext.concat(joined);

}

var filename = 'export.csv';
var blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' });

//addresses IE
if (navigator.msSaveBlob) {
    navigator.msSaveBlob(blob, filename);
} else {
    var link = document.createElement("a");
    link = document.createElement('a')
    link.href = URL.createObjectURL(blob);
    link.download = filename
    link.target = "_blank";
    link.style.visibility = 'hidden';
    link.dispatchEvent(new MouseEvent('click'))
}

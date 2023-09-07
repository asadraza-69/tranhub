var MediaCurrentTime = "";


var onClickST = "";
var onClickET = "";
var FileID ="";
$(document).ready(function () {

    var TimeCheck = "";

    var params = window.location.search.split(/\?|\&/);

    params.forEach(function (it) {
        if (it) {
            var param = it.split("=");
            result[param[0]] = param[1];
        }
    });
    FileID = (result.file_id);

  
    // GetFilesList();
    // var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    // var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    //   return new bootstrap.Tooltip(tooltipTriggerEl)
    // })
    $("[rel='data-bs-toggle']").tooltip();
    $('[data-bs-toggle="tooltip"]').tooltip();
    // GetTranscribedFileText();


var playBT = $(".vjs-big-play-button");
playBT.css({
   left:( (playBT.parent().outerWidth()-playBT.outerWidth())/2 )+"px",
   top:( (playBT.parent().outerHeight()-playBT.outerHeight())/2 )+"px"
});
});
$(document).on("click", ".Transcript", function () {
    onClickST = $(this).prev().attr("startTime");
    onClickET = $(this).prev().attr("endTime");
     onClickST2 = $(this).attr("endTime");
     player.pause(); 
     
     if(onClickET == "undefined" || onClickET == undefined){        
        player.currentTime(onClickST2);
    }
    else{
        player.currentTime(onClickET);
    }
     
});

var file_id = "";
var result = {};

var params = window.location.search.split(/\?|\&/);

params.forEach(function (it) {
    if (it) {
        var param = it.split("=");
        result[param[0]] = param[1];
    }
});
file_id = (result.file_id);
$(function () {



  

 



    /*
     * For the sake keeping the code clean and the examples simple this file
     * contains only the plugin configuration & callbacks.
     * 
     * UI functions ui_* can be located in: demo-ui.js
     */
    var fileId = "";
    var formatFile = "";
    $(document).on("click", "*[data-action=download]", function () {
        fileId = ($(this).attr('data-id'));

        $("#DownloadFile").modal('show');
        $('#formatFile').change(function (e) {
            formatFile = (e.target.value);
        });



    });
  
    $(document).on("click", ".DownloadFile", function (e) {
        e.preventDefault();  //stop the browser from following
    formatFile = $("#formatFile").val();

   new jsFileDownloader({ 
     url: "../../itrans/download_file/?file_id=" + FileID + "&file_format=" + formatFile
   })
   .then(function () {
     // Called when download ended
   })
   .catch(function (error) {
     // Called when an error occurred
     ShowNoty(error, "error");
   });
        
    });
    
   

});

// function DownloadFile(fileid, fileFormat) {
//     var url = "../../itrans/download_file/?file_id=" + fileid + "&file_format=" + fileFormat
//     window.open(url, '_blank').focus();
//     $("#DownloadFile").modal('hide');
// }

function UpdateTranscribedText() {
    UpdateTranscriptObject = $(".Transcript").map(function () {
        var StartTime = $(this).attr('starttime');
        var EndTime = $(this).attr('endtime');
       
         if (StartTime == "undefined" || StartTime == undefined){
           
            StartTime = "";
         }
       
         if (EndTime == "undefined" || EndTime == undefined){
          
            EndTime = "";
            }
          
        return [{ start_time: StartTime, end_time: EndTime, alternatives: [{ confidence: $(this).attr('confidence'), content: $(this).find('.TranscribedWord').text() }], type: $(this).attr('type') }]

        //    {start_time: "0.0", end_time: "0.11", alternatives: Array(1), type: "pronunciation"}

    }).get();



    const items = JSON.stringify(UpdateTranscriptObject);
    // var items = UpdateTranscriptObject;
    let fd = new FormData();

    fd.append("file_id", file_id);
    fd.append("items", items);
    $.ajax({
        type: "POST",
         url: "../../itrans/edit_transcribed_file/",
        data: fd,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.status) {
                alert("success");
                GetTranscribedFileText();



            }
        },
        error: function (e, x, y) {
            console.log(e);
            console.log(x);
            console.log(y);
        },
        cache: false,
        async: false
    });
    //     UpdateTranscriptObject.forEach(ArrayNew);

    // function ArrayNew(value, index, array) {
    //   console.log(value);
    // }

}
function DeleteFile(FileID) {
    var data = JSON.stringify({ id: FileID });
    $.ajax({
        type: "GET",
        url: "../../itrans/remove_file/?file_id=" + FileID,

        success: OSDeleteFile,
        error: function (e, x, y) {
            console.log(e);
            console.log(x);
            console.log(y);
        },
        cache: false,
    });
}

function OSDeleteFile(data, success) {
    if (data.data != "") {

        GetFilesList();
    } else {
        onError();
    }
}


function onError() {

    alert('Something Went Wrong!');
    return false;
}





function GetTranscribedFileConfidence() {


    var result = {};

    var params = window.location.search.split(/\?|\&/);

    params.forEach(function (it) {
        if (it) {
            var param = it.split("=");
            result[param[0]] = param[1];
        }
    });
    var confidenceFileId = (result.file_id);

    $.ajax({
        type: "GET",
        url: "../../itrans/get_confidence_level/?file_id=" + confidenceFileId,
        processData: false,
        contentType: false,
        data: null,
        success: function (data, success) {
            if (data.status != false) {
                var obj = (data.confidence_level);

                // confidence_level:

                var FC = obj.fairly_confident.split('%')[0];
                var SC = obj.slightly_confident.split('%')[0];
                var VC = obj.very_confident.split('%')[0];

                $("#VeryConfident").css('width', VC + '%');
                $("#FairlyConfident").css('width', FC + '%');
                $("#SlightlyConfident").css('width', SC + '%');

                $("#VeryConfident").find('span').html(VC + '%');
                $("#FairlyConfident").find('span').html(FC + '%');
                $("#SlightlyConfident").find('span').html(SC + '%');

                $("#VeryConfidentPercent").html(VC + '%');
                $("#FairlyConfidentPercent").html(FC + '%');
                $("#SlightlyConfidentPercent").html(SC + '%');
                // fairly_confident: "8.4% | 11 words"
                // slightly_confident: "2.5% | 3 words"
                // very_confident: "89:1% | 116 words"



            }
        },
        error: function (e, x, y) {
            console.log(e);
            console.log(x);
            console.log(y);
        },
        cache: false,
        async: false
    });
}



function GetTranscribedFileText() {


   

    $.ajax({
        type: "GET",
        url: "../../itrans/get_confidence_level/?file_id=" + FileID,
        processData: false,
        contentType: false,
        data: null,
        success: function (data, success) {
            if (data.status != false) {

            
                
                $("#TranscibedFileTextPreviewNew").empty();
                var object = (data.items);
                //   alternatives: Array(1)
                //   0:
                //   confidence: "0.991"
                //   content: "if"
                //   __proto__: Object
                //   length: 1
                //   __proto__: Array(0)
                //   end_time: "0.11"
                //   start_time: "0.0"
                //   type: "pronunciation"

                jQuery.each(object, function (i, val) {

                    var AltObject = val.alternatives;
                
                    var StartTime = (val.start_time);
                    var EndTime = (val.end_time);
                    var Type = (val.type);
                 console.log(StartTime + "  StartTime");
                 if(StartTime == ""){
                    StartTime = "undefined"
                 }
                 if(EndTime == ""){
                    EndTime = "undefined"
                 }
                    $("#TranscibedFileTextPreviewNew").append("<span class='Transcript' starttime=" + StartTime + " endtime=" + EndTime + " value=" + AltObject[0].content + " confidence=" + AltObject[0].confidence + " type=" + Type + "><span class='startTime'>" + StartTime + "</span><span class='TranscribedWord' starttime=" + StartTime + " endtime=" + EndTime + " value=" + AltObject[0].content + ">" + AltObject[0].content + "</span><span class='endTime'>" + EndTime + "</span></span>");
                });
                TimeCheck = $(".TranscribedWord").map(function () {
                    return $(this);
                }).get();

            }
        },
        error: function (e, x, y) {
            console.log(e);
            console.log(x);
            console.log(y);
        },
        cache: false,
        async: false
    });
}
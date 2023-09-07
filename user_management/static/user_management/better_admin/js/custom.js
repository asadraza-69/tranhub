var JobId= "";
var TimeCheck = "";
var onClickST = "";
var onClickET = "";
$(document).ready(function () {

  // GetFilesList();
  // var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  // var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  //   return new bootstrap.Tooltip(tooltipTriggerEl)
  // })
  $("[rel='data-bs-toggle']").tooltip();
  $('[data-bs-toggle="tooltip"]').tooltip();

  getAndRenderDynamicTable('../../itrans/file_listview', 'dynamicTable');
  
});
let timerId = setInterval(() => getAndRenderDynamicTable('../../itrans/file_listview', 'dynamicTable'), 60000);



$(function () {
  $('a[data-action=download]').removeAttr('href');
  /*
   * For the sake keeping the code clean and the examples simple this file
   * contains only the plugin configuration & callbacks.
   * 
   * UI functions ui_* can be located in: demo-ui.js
   */
  $(document).on("click", "a[data-action=view_invoice]", function () {
    var id  = $(this).attr('data-id')
    console.log("id",id)
    $.ajax({
      type: "GET",
      url: "/stripe_payments/invoice_detail/?project_id="+id,
      data: $(this).serialize,
      dataType: "json",
      contentType: "application/json; charset=utf-8",
      success: function (data) {
          console.log(data);
         var inv_data = data.data;
           console.log("test files ",inv_data)
          $('#table').html('');
          var files = "";
          var roww="";
          var services = "";
          // $.each(inv_data.length, function(index, value){
            files = inv_data.file;
            services = inv_data.services[0];
            Object.keys(files).forEach(function(key) {
  
             
              var fileDetails= files[key];
            console.log(fileDetails + "  fileDetails");
           
             roww += '<tr>'
           + '<td data-toggle="tooltip" data-placement="top" title="Tooltip on top">' + `${fileDetails['name']}` + '</td>'
             + '<td>' + `${fileDetails["length"]}` + '</td>'
            + '<td  class="text-end"> $ ' + `${fileDetails['amount']}` + '</td>'        
            + '</tr>'
           
          // //   services = `${data.data['services'][0]}`
          // // });
          // roww = '<tr>'
          //  + '<td>' + `${inv_data['name']}` + '</td>'
          //    + '<td>' + `${inv_data["length"]}` + '</td>'
          //   + '<td class="text-end"> $ ' + `${inv_data['amount']}` + '</td>'        
          //   + '</tr>'
           
        });  
$("[rel='tooltip']").tooltip();
         
  
     
          $.each( services, function( key, value ) {
            key= key.replace(/_/g, ' ');
            roww += '<tr class="bg-light">'
            + '<td colspan="2"><small>' + key + '</small></td>'
              + '<td class="text-end"><small>$ ' + value + '</small></td>'
                    
             + '</tr>'
        });
  
         var Dsc = `${inv_data.estimated_total}`;
        if(Dsc != "undefined"){
        roww += '<tr>'
        + '<td colspan="1">Estimated Amt.</td>'
        
         + '<td colspan="2" class="text-end">' + `${inv_data.estimated_total}` + '</td>'
         + '</tr>'
         };
         var Dsc = `${inv_data.discount_voucher}`;
        if(Dsc != "undefined"){
          roww += '<tr>'
          + '<td colspan="1">Discount</td>'
          
           + '<td colspan="2" class="text-end">- ( ' + `${inv_data.discount_voucher}` + ' )</td>'        
           + '</tr>'
        };
    
        
   
         
          $('#table').append(roww)
          $('#total').html('');
   
            $('#total').append(`<strong>$ ${inv_data.total}</strong>`)
         
  
        
      }
  });
    $("#viewInovice").modal('show');
   
  });
  var fileId = "";
  var formatFile = "";
  $(document).on("click", "a[data-action=download]", function () {
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
     url: "../../itrans/download_file/?file_id=" + fileId + "&file_format=" + formatFile
   })
   .then(function () {
     // Called when download ended
   })
   .catch(function (error) {
     // Called when an error occurred
     ShowNoty(error, "error");
   });

});

  $(document).on("click", "#TextQualityStats", function () {
    $("#TextQualityStatsModals").modal('show');
    GetTranscribedFileConfidence();
  });
  $('#drag-and-drop-zone').dmUploader({ //
    url: '/itrans/save_file/',
    multiple: false,
    // maxFileSize: 3000000, // 3 Megs 
    onDragEnter: function () {
      // Happens when dragging something over the DnD area
      this.addClass('active');
    },
    onDragLeave: function () {
      // Happens when dragging something OUT of the DnD area
      this.removeClass('active');
    },
    onInit: function () {
      // Plugin is ready to use
      ui_add_log('Penguin initialized :)', 'info');
    },
    onComplete: function () {
      // All files in the queue are processed (success or error)
      ui_add_log('All pending tranfers finished');
    },
    onNewFile: function (id, file) {
      // When a new file is added using the file selector or the DnD area
      ui_add_log('New file added #' + id);
      ui_multi_add_file(id, file);
    },
    onBeforeUpload: function (id) {
      // about tho start uploading a file
      ui_add_log('Starting the upload of #' + id);
      ui_multi_update_file_status(id, 'uploading', 'Uploading...');
      ui_multi_update_file_progress(id, 0, '', true);
    },
    onUploadCanceled: function (id) {
      // Happens when a file is directly canceled by the user.
      ui_multi_update_file_status(id, 'warning', 'Canceled by User');
      ui_multi_update_file_progress(id, 0, 'warning', false);
    },
    onUploadProgress: function (id, percent) {
      // Updating file progress
      ui_multi_update_file_progress(id, percent);
    },
    onUploadSuccess: function (id, data, xhr, status, message) {
     
      // A file was successfully uploaded
    
     if(data.errors.length > 0){
      ShowNoty("File Upload Failed! " + data.errors  , "error");
      ui_multi_update_file_status(id, 'danger', 'Upload Failed');
      ui_multi_update_file_progress(id, 0, 'danger', false);
    
     }
     else{
      ui_add_log('Server Response for file #' + id + ': ' + JSON.stringify(data));
      ui_add_log('Upload of file #' + id + ' COMPLETED', 'success');
      ui_multi_update_file_status(id, 'success', 'Upload Complete');
      ui_multi_update_file_progress(id, 100, 'success', false);
      $("#ConfimationText").html("<span job_id="+ data.job_id +">Your <strong>" + data.length + "</strong> file will cost <strong> $ " + data.charge + "</strong> .</br>Do you want to transcribe the file?</span>");
      $("#ConfimationModal").modal('show');
     }
   
      // getAndRenderDynamicTable('../../itrans/file_listview', 'dynamicTable');
    },
    onUploadError: function (id, xhr, status, message) {
      ui_multi_update_file_status(id, 'danger', message);
      ui_multi_update_file_progress(id, 0, 'danger', false);
    },
    onFallbackMode: function () {
      // When the browser doesn't support this plugin :(
      ui_add_log('Plugin cant be used here, running Fallback callback', 'danger');
    },
    onFileSizeError: function (file) {
      ui_add_log('File \'' + file.name + '\' cannot be added: size excess limit', 'danger');
    }
  });
});

$(document).on("click", ".ContinueTranscribe", function () {

var jobid = $("#ConfimationText span").attr('job_id');
  ConfirmTranscibing(jobid);
});

$(document).on("click", ".CancelTranscribe", function () {
   $("#files").empty();
});
function ConfirmTranscibing(jobid) {
  
  let jobnumber = new FormData();

  jobnumber.append("job_id", jobid);
  if(jobnumber != undefined){
    $.ajax({
      type: "POST",
      url: "../../itrans/set_job_status/",
      data: jobnumber,
      processData: false,
      contentType: false,
      success: OSConfirmTranscibing,
      error: function (e, x, y) {
        console.log(e);
        console.log(x);
        console.log(y);
      },
      cache: false,
    });
  }
  else{
    ShowNoty("Something Went Wrong!","error");
  }

}
function OSConfirmTranscibing(data, success) {
  if (data.status == true) {
    $("#ConfimationModal").modal('hide');
    ShowNoty("File Uploaded successfully!", "alert");
    getAndRenderDynamicTable('../../itrans/file_listview', 'dynamicTable');
  } else {
    $("#ConfimationModal").modal('hide');
    ShowNoty(data.errors, "alert");
  }
}

function DeleteFile(fileid) {
  var data = JSON.stringify({ id: fileid });
  $.ajax({
    type: "GET",
    url: "../../itrans/remove_file/?file_id=" + fileid,
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
  ShowNoty("Something Went Wrong!", "error");
  return false;
}
// function DownloadFile(fileid, fileFormat) {
//   var url = "../../itrans/download_file/?file_id=" + fileid + "&file_format=" + fileFormat
//   window.open(url, '_blank').focus();
//   $("#DownloadFile").modal('hide');
// }
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

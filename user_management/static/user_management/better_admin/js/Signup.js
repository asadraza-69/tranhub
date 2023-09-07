var pymentHtml;
$(document).ready(function () {
  $('body').tooltip({
   
});
  pymentHtml = $('#hidePyement').html();
  // console.log('html',pymentHtml)
  $("#phone_numberold").on("change paste keyup", function () {
    let value = $(this).val();
    $("#phone_number").attr("value", value);
    $("#phone_number").val(value);
  });

  var btnFinish = $("<button></button>")
    .text("View Projects")
    .addClass("btn btn-warning sw-btn-group-extra d-none")
    .on("click", function () {
      window.location = '/user_management/main_dashboard/';
    });
  var btnCancel = $("<button></button>")
    .text("Create new project")
    .addClass("btn btn-danger sw-btn-group-extra d-none")
    .on("click", function () {
      clearQ();
      $('#smartwizard').smartWizard("stepState", [1,2], "");
      $("#smartwizard").smartWizard("reset");
      $("#projectname").val("");
    });

  $("#smartwizard").smartWizard({
    selected: 0, // Initial selected step, 0 = first step
    theme: "dots", // theme for the wizard, related css need to include for other than default theme
    justified: true, // Nav menu justification. true/false
    darkMode: false, // Enable/disable Dark Mode if the theme supports. true/false
    autoAdjustHeight: true, // Automatically adjust content height
    cycleSteps: false, // Allows to cycle the navigation of steps
    backButtonSupport: true, // Enable the back button support
    enableURLhash: false, // Enable selection of the step based on url hash
    transition: {
      animation: "slide-horizontal", // Effect on navigation, none/fade/slide-horizontal/slide-vertical/slide-swing
      speed: "400", // Transion animation speed
      easing: "", // Transition animation easing. Not supported without a jQuery easing plugin
    },
    toolbarSettings: {
      toolbarPosition: "bottom", // none, top, bottom, both
      toolbarButtonPosition: "center", // left, right, center
      showNextButton: true, // show/hide a Next button
      showPreviousButton: true, // show/hide a Previous button
      // toolbarExtraButtons: [], // Extra buttons to show on toolbar, array of jQuery input/buttons elements
    toolbarExtraButtons: [btnFinish],
    },
    anchorSettings: {
      anchorClickable: true, // Enable/Disable anchor navigation
      enableAllAnchors: false, // Activates all anchors clickable all times
      markDoneStep: true, // Add done state on navigation
      markAllPreviousStepsAsDone: true, // When a step selected by url hash, all previous steps are marked done
      removeDoneStepOnNavigateBack: false, // While navigate back done step after active step will be cleared
      enableAnchorOnDoneStep: true, // Enable/Disable the done steps navigation
    },
    keyboardSettings: {
      keyNavigation: false, // Enable/Disable keyboard navigation(left and right keys are used if enabled)
      keyLeft: [37], // Left key code
      keyRight: [39], // Right key code
    },
    lang: {
      // Language variables for button
      next: "Next",
      previous: "Previous",
    },
    disabledSteps: [], // Array Steps disabled
    errorSteps: [], // Highlight step with errors
    hiddenSteps: [], // Hidden steps,
    onShowStep: onStepLoad
  });
  $(".sw-btn-next").hide();
  $(".sw-btn-prev").hide(); 
  $("#projectname").change(function () {
    $(".msg-projectname").hide();

   
if($(this).val() != ""){
  $(".sw-btn-next").removeClass("disabled");
}
else{
  $(".sw-btn-next").addClass("disabled");
}

    
  });



  // Initialize the leaveStep event
  // $("#smartwizard").on("leaveStep", function(e, anchorObject, currentStepIndex, nextStepIndex, stepDirection) {
  //    return confirm("Do you want to leave the step " + currentStepIndex + "?");
  // });
  $('.sw-btn-next').click(function() {
    $('.nav-pills > .active').prev('li').find('a').trigger('click');
  });
  
 


  $("#smartwizard").on("leaveStep",function (e, anchorObject, currentStepIndex, nextStepIndex, stepDirection) {

    console.log(currentStepIndex, nextStepIndex);
    if (currentStepIndex == 0 && nextStepIndex == 1) {
      $(".sw-btn-next").hide();

    }
    if (nextStepIndex == 1) {
      
    
     
      // $(".sw-btn-next").addClass("disabled");
      // $(".sw-btn-prev").addClass("disabled");
       $(".sw-btn-next").hide();
       $(".sw-btn-prev").hide();
     
      $('#smartwizard').smartWizard("stepState", [2], "");
      $(".sw-btn-next").hide();

      
    }
   


      if (currentStepIndex == 1 && nextStepIndex != 0) {
      
       
        //here is the final step: Note: 0,1,2
        $(".sw-btn-group-extra").removeClass("d-none");
        $(".sw-btn-next").hide();
        $(".sw-btn-prev").hide();
       
       
      } else {
        $(".sw-btn-group-extra").addClass("d-none");
      }
    
    //   if(anchorObject.prevObject.length - 1 == nextStepIndex){
    //     e.preventDefault()
    //     $(".sw-btn-next").addClass("disabled");
    //     $(".sw-btn-prev").addClass("disabled");
     
    // }
      validateSteps(currentStepIndex);
 
  
    });
    function onStepLoad(obj, context) {
      debugger;
      alert("Leaving step " + context.fromStep + " to go to step " + context.toStep);
      return validateSteps(context.fromStep); // return false to stay on step and true to continue navigation 
  }
    // console.log(currentStepIndex + "  currentStepIndex step");
    // validateSteps(currentStepIndex);

    // if (isStepValid == false) {
    //   return false;
    // }

    // console.log(isStepValid);

  var isStepValid = true;

  function validateSteps(step) {
    // validate step 1
  
    if (step == 0) {
    
      if (validateStep0() == false) {
        isStepValid = false;
        ShowNoty(
          "Please correct the errors in step " + step + " and click next.",
          "error"
        );
      } else {
        isStepValid = true;
      
      }
    
    }
   
    if (step == 1) {
   
      if (validateStep1() == false) {
        isStepValid = false;
        ShowNoty(
          "Please correct the errors in step " + step + " and click next.",
          "error"
        );
      }
       else {
        isStepValid = true;
        $(".sw-btn-prev").addClass("disabled");
      
      }
    }

    // validate step3
    // if(step == 3){
    //   if(validateStep3() == false ){
    //     isStepValid = false;
    //     $('#wizard').smartWizard('showMessage','Please correct the errors in step'+step+ ' and click next.');
    //     $('#wizard').smartWizard('setError',{stepnum:step,iserror:true});
    //   }else{
    //     $('#wizard').smartWizard('hideMessage');
    //     $('#wizard').smartWizard('setError',{stepnum:step,iserror:false});
    //   }
    // }

    return isStepValid;
  }
  
  $(".summary-edit-link").click(function () {
    $(".sw-btn-prev").trigger("click");
  });
  $("input[name=ServiceTypeRB]").click(function () {
    if ($("#ServiceType1").prop("checked")) {
       $(".TranscriptionServicesContainer").show();
      Total_CCS = 0
      $('#Total_closed_captioning_services_val').html('$ <span class="TotalVal">'+ Total_CCS.toFixed(2)+'</span>');  
      if ($("#TimeStampRB1").prop("checked")) {
 
        Total_TimeStamping_Amt = 0
        $('#Total_Timestamping_val').html('$ <span class="TotalVal">'+ Total_TimeStamping_Amt.toFixed(2)+'</span>');  
      } else if ($("#TimeStampRB2").prop("checked")) {
        Total_TimeStamping_Amt = $("#on_speaker_change_val").text();
        Total_TimeStamping_Amt = Total_TimeStamping_Amt*sumMin;
        $('#Total_Timestamping_val').html('$ <span class="TotalVal">'+ Total_TimeStamping_Amt.toFixed(2)+'</span>');  
      }
      else if ($("#TimeStampRB3").prop("checked")) {
        Total_TimeStamping_Amt = $("#every_2_minutes_val").text();
        Total_TimeStamping_Amt = Total_TimeStamping_Amt*sumMin;
        $('#Total_Timestamping_val').html('$ <span class="TotalVal">'+ Total_TimeStamping_Amt.toFixed(2)+'</span>');  
      }
      if ($("#VerbatimRB1").prop("checked")) {
 
        Total_Verbatim_Amt = 0
        $('#Total_Verbatim_val').html('$ <span class="TotalVal">'+ Total_Verbatim_Amt.toFixed(2)+'</span>');  
      } else if ($("#VerbatimRB2").prop("checked")) {
        Total_Verbatim_Amt = $("#verbatim_val").text();
        Total_Verbatim_Amt = Total_Verbatim_Amt*sumMin;
        $('#Total_Verbatim_val').html('$ <span class="TotalVal">'+ Total_Verbatim_Amt.toFixed(2)+'</span>');  
      }
      $('#ClosedCaptioningServicesSummary').hide();
      $('#ClosedCaptioningServicesSummary').empty(); 
    } else if ($("#ServiceType2").prop("checked")) {
       $(".TranscriptionServicesContainer").hide();
      Total_CCS = CCS_val*sumMin;
      $('#ClosedCaptioningServicesSummary').show();
      $('#Total_closed_captioning_services_val').html('$ <span class="TotalVal">'+ Total_CCS.toFixed(2)+'</span>');  
      $('#ClosedCaptioningServicesSummary').html('<td>Closed Captioning Services</td><td style="text-align:right">$ '+ Total_CCS.toFixed(2)+'<input type="hidden" class="ServiceTypeInput" name="closed_captioning_services" value="'+ Total_CCS.toFixed(2)+'" /></td>');  
      Total_TimeStamping_Amt = 0
      $('#Total_Timestamping_val').html('$ <span class="TotalVal">'+ Total_TimeStamping_Amt.toFixed(2)+'</span>');  
      Total_Verbatim_Amt = 0
      $('#Total_Verbatim_val').html('$ <span class="TotalVal">'+ Total_Verbatim_Amt.toFixed(2)+'</span>'); 
    } 
    GetSubTotal();
  });



  $("input[name=TimeStampRB]").click(function () {
    if ($("#TimeStampRB1").prop("checked")) {
 
      Total_TimeStamping_Amt = 0
      $('#Total_Timestamping_val').html('$ <span class="TotalVal">'+ Total_TimeStamping_Amt.toFixed(2)+'</span>'); 
      $('#OnSpeakerChangeSummary').hide();
      $('#Every2MinutesSummary').hide();
       
    } else if ($("#TimeStampRB2").prop("checked")) {
      $('#OnSpeakerChangeSummary').show();
      $('#Every2MinutesSummary').hide();
      Total_TimeStamping_Amt = $("#on_speaker_change_val").text();
      Total_TimeStamping_Amt = Total_TimeStamping_Amt*sumMin;
      $('#Total_Timestamping_val').html('$ <span class="TotalVal">'+ Total_TimeStamping_Amt.toFixed(2)+'</span>');  
      $('#OnSpeakerChangeSummary').html('<td>Timestamping On Speaker Change</td><td style="text-align:right">$ '+ Total_TimeStamping_Amt.toFixed(2)+'<input type="hidden" class="ServiceTypeInput" name="on_speaker_change" value="'+ Total_TimeStamping_Amt.toFixed(2)+'" /></td>');  
    }
    else if ($("#TimeStampRB3").prop("checked")) {
      $('#OnSpeakerChangeSummary').hide();
      $('#Every2MinutesSummary').show();
      Total_TimeStamping_Amt = $("#every_2_minutes_val").text();
      Total_TimeStamping_Amt = Total_TimeStamping_Amt*sumMin;
      $('#Total_Timestamping_val').html('$ <span class="TotalVal">'+ Total_TimeStamping_Amt.toFixed(2)+'</span>');  
      $('#Every2MinutesSummary').html('<td>Timestamping Every 2 Minutes</td><td style="text-align:right">$ '+ Total_TimeStamping_Amt.toFixed(2)+'<input type="hidden" class="ServiceTypeInput" name="every_2_minutes" value="'+ Total_TimeStamping_Amt.toFixed(2)+'" /></td>'); 
    }
    GetSubTotal();
  
  });

  

  $("input[name=VerbatimRB]").click(function () {
    if ($("#VerbatimRB1").prop("checked")) {
      $('#VerbatimSummary').hide();
      Total_Verbatim_Amt = 0
      $('#Total_Verbatim_val').html('$ <span class="TotalVal">'+ Total_Verbatim_Amt.toFixed(2)+'</span>');  
    } else if ($("#VerbatimRB2").prop("checked")) {
      $('#VerbatimSummary').show();
      Total_Verbatim_Amt = $("#verbatim_val").text();
      Total_Verbatim_Amt = Total_Verbatim_Amt*sumMin;
      $('#Total_Verbatim_val').html('$ <span class="TotalVal">'+ Total_Verbatim_Amt.toFixed(2)+'</span>');  
      $('#VerbatimSummary').html('<td>Verbatim</td><td style="text-align:right">$ '+ Total_Verbatim_Amt.toFixed(2)+'<input type="hidden" class="ServiceTypeInput" name="verbatim" value="'+ Total_Verbatim_Amt.toFixed(2)+'" /></td>'); 
    }
    GetSubTotal();
  });


  
  $("input[name=rush_my_order]").click(function () {
    if ($("#UrgentOrder").prop("checked")) {
      $('#RushMyOrderSummary').show();
      Total_RushOrder_Amt = $("#UrgentOrder_Val").text();
      Total_RushOrder_Amt = Total_RushOrder_Amt*sumMin;
      $('#Total_rush_my_order_val').html('$ <span class="TotalVal">'+ Total_RushOrder_Amt.toFixed(2)+'</span>'); 
      $('#RushMyOrderSummary').html('<td>Rush My Order</td><td style="text-align:right">$ '+ Total_RushOrder_Amt.toFixed(2)+'<input type="hidden" class="ServiceTypeInput" name="rush_my_order" value="'+ Total_RushOrder_Amt.toFixed(2)+'" /></td>'); 
    } else{
      $('#RushMyOrderSummary').hide();
       Total_RushOrder_Amt = 0
      $('#Total_rush_my_order_val').html('$ <span class="TotalVal">'+ Total_RushOrder_Amt.toFixed(2)+'</span>'); 
    }
    GetSubTotal();
  });
  $("input[name=instant_first_draft]").click(function () {
    if ($("#InstantService").prop("checked")) {
      $('#InstantFirstDraftSummary').show();
      Total_InstantDraft_Amt = $("#InstantServiceVal").text();
      Total_InstantDraft_Amt = Total_InstantDraft_Amt*sumMin;
      $('#Total_instant_first_draft_val').html('$ <span class="TotalVal">'+ Total_InstantDraft_Amt.toFixed(2)+'</span>'); 
      $('#InstantFirstDraftSummary').html('<td>Instant First Draft</td><td style="text-align:right">$ '+ Total_InstantDraft_Amt.toFixed(2)+'<input type="hidden" class="ServiceTypeInput" name="instant_first_draft" value="'+ Total_InstantDraft_Amt.toFixed(2)+'" /></td>'); 
    } else{
      $('#InstantFirstDraftSummary').hide();
      Total_InstantDraft_Amt = 0
      $('#Total_instant_first_draft_val').html('$ <span class="TotalVal">'+ Total_InstantDraft_Amt.toFixed(2)+'</span>'); 
    }
    GetSubTotal();
  });
  $("#SaveCardDetails").click(function () {
    if ($(this).prop("checked")) {
      $(this).val("true");
    } else {
      $(this).val("false");
    }
  });

  InitializeUploader();
});

function clearQ() {
  // clear any files currently in queue
  $('.media').remove();
  // restore 'No files uploaded' message in user-visible file queue
  $('#files').find('li.empty').fadeIn(); 
  // disable "Clear Queue" button until more files have been uploaded
  $("#qClearButton").prop("disabled", true);
  // get reference to dmUploader plugin in order to access queue-related variables
  var myUploader = $('#drag-and-drop-zone').dmUploader().data();
  myUploader.queue = [];
  myUploader.queuePos = -1;
  myUploader.activeFiles = 0;
  $(".SubTotalDiv").hide();
  GetSubTotal();

}
var file_paths = [];
function validateStep0() {
  var isValid = true;
  var projectname = $("#projectname").val();
  if ($("#files").children().length == 1) {
    isValid = false;
    $(".msg-filesupload").html("Please upload files").show();
  } else if (
    $("#files").children().length > 1 &&
    !projectname &&
    projectname.length <= 0
  ) {
    isValid = false;
    $(".msg-projectname").html("Please enter project name").show();
  } else {
    isValid = true;
    $(".ServiceType").show();
    $(".msg-filesupload").html("").hide();
    $(".msg-projectname").html("").hide();
  }

  return isValid;
}

function validateStep1() {
 
  var isValid = false;
  if($(".SignUpForm").length < 0){

 
  var UserEmail = $("#UserEmail").val();
  if (!UserEmail && UserEmail.length <= 0) {
    isValid = false;
    $(".msg-UserEmail").html("Please enter email address").show();
  } else {
    isValid = true;    
    $(".msg-UserEmail").html("").hide();
  }

  var Signup_password = $("#Signup_password").val();
  if (!Signup_password && Signup_password.length <= 0) {
    isValid = false;
    $(".msg-Signup_password").html("Please enter password").show();
  } else {
    isValid = true;    
    $(".msg-Signup_password").html("").hide();
  }


  var first_name = $("#first_name").val();
  if (!first_name && first_name.length <= 0) {
    isValid = false;
    $(".msg-first_name").html("Please enter first name").show();
  } else {
    isValid = true;    
    $(".msg-first_name").html("").hide();
  }



  var last_name = $("#last_name").val();
  if (!last_name && last_name.length <= 0) {
    isValid = false;
    $(".msg-last_name").html("Please enter last name").show();
  } else {
    isValid = true;    
    $(".msg-last_name").html("").hide();
  }


  var company_name = $("#company_name").val();
  if (!company_name && company_name.length <= 0) {
    isValid = false;
    $(".msg-company_name").html("Please enter company name").show();
  } else {
    isValid = true;    
    $(".msg-company_name").html("").hide();
  }

  
  var phone_number = $("#phone_number").val();
  if (!phone_number && phone_number.length <= 0) {
    isValid = false;
    $(".msg-phone_number").html("Please enter phone number").show();
  } else {
    isValid = true;    
    $(".msg-phone_number").html("").hide();
  }

}else{
  isValid = true;
}
  return isValid;
}
var fileUploadData = "";
var Total_CCS =0;
var sumMin = 0;
var CCS_val =0;
var  Total_TimeStamping_Amt=0;
var Total_Verbatim_Amt = 0;
var Total_RushOrder_Amt = 0;
var Total_InstantDraft_Amt = 0;
var SubTotal =0;
function InitializeUploader() {
  $("#drag-and-drop-zone").dmUploader({
    //
    url: "/itrans/upload_file/",
    multiple: true,
    extFilter: ["amr", "flac", "wav", "ogg", "mp3", "mp4", "webm"],
    onFileExtError:function(){
      ShowNoty("Invalid File type!", "error");
      
    },
    // maxFileSize: 3000000, // 3 Megs
    onDragEnter: function () {
      // Happens when dragging something over the DnD area
      this.addClass("active");

    },
    onDragLeave: function () {
      // Happens when dragging something OUT of the DnD area
      this.removeClass("active");
    },
    onInit: function () {
      // Plugin is ready to use
      ui_add_log("Penguin initialized :)", "info");
    },
    onComplete: function () {
      // All files in the queue are processed (success or error)
      ui_add_log("All pending transfers finished");
    },
    onNewFile: function (id, file) {
      // When a new file is added using the file selector or the DnD area
      ui_add_log("New file added #" + id);
      ui_multi_add_file(id, file);
      
    
    },
    onBeforeUpload: function (id) {
      // about tho start uploading a file
      ui_add_log("Starting the upload of #" + id);
      ui_multi_update_file_status(id, "uploading", "Uploading...");
      ui_multi_update_file_progress(id, 0, "", true);
     
    },
    onUploadCanceled: function (id) {
      // Happens when a file is directly canceled by the user.
      ui_multi_update_file_status(id, "warning", "Canceled by User");
      ui_multi_update_file_progress(id, 0, "warning", false);
    },
    onUploadProgress: function (id, percent) {
   
      // Updating file progress
      ui_multi_update_file_progress(id, percent);
      $(".tab-content").css("height", "auto");
      
  
    },
    onUploadSuccess: function (id, data, xhr, status, message) {
      // A file was successfully uploaded

      if (data.errors.length > 0) {
        ShowNoty("File Upload Failed! " + data.errors, "error");
        ui_multi_update_file_status(id, "danger", "Upload Failed");
        ui_multi_update_file_progress(id, 0, "danger", false);
      }
       else {
        ui_add_log(
          "Server Response for file #" + id + ": " + JSON.stringify(data)
        );
        ui_add_log("Upload of file #" + id + " COMPLETED", "success");
        ui_multi_update_file_status(id, "success", "Upload Complete");
        ui_multi_update_file_progress(id, 100, "success", false);
        // $("#ConfimationText").html("<span job_id="+ data.job_id +">Your <strong>" + data.length + "</strong> file will cost <strong> $ " + data.charge + "</strong> .</br>Do you want to transcribe the file?</span>");
        // $("#ConfimationModal").modal('show');
        fileUploadData = data;
        file_paths.push(data.file_path);

       
       
       
        $(".msg-filesupload").html("").hide();
        
        $(".ServiceType").show();
        $(".SubTotalDiv").show();
        
        $(".tab-content").css("height", "auto");
        // $("#InstantQuote tbody").append("<tr><td>"+data.filename+"</td><td style='text-align: right;'>$ <span class='Project_charges'>"+data.file_charge+"</span></td></tr>")
        $("#closed_captioning_services_val").text(data.closed_captioning_services);
        
        $("#on_speaker_change_val").text(data.on_speaker_change);
        $("#every_2_minutes_val").text(data.every_2_minutes);
        $("#verbatim_val").text(data.verbatim);
        $("#UrgentOrder_Val").text(data.rush_my_order);
        $("#InstantServiceVal").text(data.instant_first_draft);
        $('#RatePerMin').text('($ ' + data.file_charge_minute + " / min)");
 

        
  
  $("#uploaderFile"+id).find(".media-body p").addClass("DMFileName");
  $("#uploaderFile"+id).find(".media-body .DMFileName").append("<i class='fa fa-trash'></i>");
  
  $("#uploaderFile"+id).find(".media-body .progressContainer").after("<span class='FileCharges'><span class='InMinutes'>"+data.file_min+"</span> m ("+data.file_length+")</span><span class='FileCharges'>$ <span class='fileChargesAmt'>"+data.file_charge+"</span> </span>");
  var proName =  $("#projectname").val();
  
  if(proName!= '') {
    $(".sw-btn-next").removeClass("disabled");

  } 
  
  // var sum = 0;
  // $(".fileChargesAmt").each(function(){
  //   sum += parseFloat($(this).text());
  // });
  // $('#SubTotal').text('$ ' + sum);  

  // SubTotal = sum;



  // sumMin = 0;
  // $(".InMinutes").each(function(){
  //   sumMin += parseFloat($(this).text());
  // });
  // $('#Total_Minutes').text(sumMin+ ' m');  


 CCS_val = (data.closed_captioning_services);



GetSubTotal();

}
      // $("#uploaderFile"+id).find(".progress").remove();
      // getAndRenderDynamicTable('../../itrans/file_listview', 'dynamicTable');
    },
    onUploadError: function (id, xhr, status, message) {
      ui_multi_update_file_status(id, "danger", message);
      ui_multi_update_file_progress(id, 0, "danger", false);
      $(".tab-content").css("height", "auto");
    },
    onFallbackMode: function () {
      // When the browser doesn't support this plugin :(
      ui_add_log(
        "Plugin cant be used here, running Fallback callback",
        "danger"
      );
    },
    onFileSizeError: function (file) {
      ui_add_log(
        "File '" + file.name + "' cannot be added: size excess limit",
        "danger"
      );
    },
  });
}


$(document).on("click",".DMFileName .fa-trash",function() {
  $(this).closest('.media').remove();
  $(".sw-btn-next").addClass("disabled");
 
  GetSubTotal();
});

  $("#projectname").change(function () {
    $(".error").hide();
  });
  function GetSubTotal() {

  
    sumMin = 0;
    $(".InMinutes").each(function(){
      sumMin += parseFloat($(this).text());
    });
    $('#Total_Minutes').text(sumMin+ ' m');  
    
    
    if ($("#ServiceType2").prop("checked")) {
      Total_CCS = CCS_val*sumMin;
      $('#ClosedCaptioningServicesSummary').show();
      $('#Total_closed_captioning_services_val').html('$ <span class="TotalVal">'+ Total_CCS.toFixed(2) +'</span>');  
      $('#ClosedCaptioningServicesSummary').html('<td>Closed Captioning Services</td><td style="text-align:right">$ '+ Total_CCS.toFixed(2)+'<input type="hidden" class="ServiceTypeInput" name="closed_captioning_services" value="'+ Total_CCS.toFixed(2)+'" /></td>');  
     
      
    }
    else{
      $('#ClosedCaptioningServicesSummary').hide();
      Total_CCS = 0;
      $('#Total_closed_captioning_services_val').html('$ <span class="TotalVal">'+ Total_CCS.toFixed(2) +'</span>'); 
      $('#ClosedCaptioningServicesSummary').empty(); 
    }
      
      
    if ($("#UrgentOrder").prop("checked")) {
      Total_RushOrder_Amt = $("#UrgentOrder_Val").text();
      Total_RushOrder_Amt = Total_RushOrder_Amt*sumMin;
      $('#Total_rush_my_order_val').html('$ <span class="TotalVal">'+ Total_RushOrder_Amt.toFixed(2)+'</span>');
     
    } else{
      Total_RushOrder_Amt = 0
      $('#Total_rush_my_order_val').html('$ <span class="TotalVal">'+ Total_RushOrder_Amt.toFixed(2)+'</span>');  
    }
    
    if ($("#InstantService").prop("checked")) {
      Total_InstantDraft_Amt = $("#InstantServiceVal").text();
      Total_InstantDraft_Amt = Total_InstantDraft_Amt*sumMin;
      $('#Total_instant_first_draft_val').html('$ <span class="TotalVal">'+ Total_InstantDraft_Amt.toFixed(2)+'</span>'); 
    } else{
      Total_InstantDraft_Amt = 0
      $('#Total_instant_first_draft_val').html('$ <span class="TotalVal">'+ Total_InstantDraft_Amt.toFixed(2)+'</span>'); 
    }
    
    
    
    
      var sum = 0;
    $(".fileChargesAmt").each(function(){
      sum += parseFloat($(this).text());
    });
    $('#SubTotal').text('$ ' + sum);  
    
    SubTotal = sum;
    
    
    
      var TotalExtraCharges = 0;
      $(".TotalVal").each(function(){
        TotalExtraCharges += parseFloat($(this).text());
      });
     
      TotalExtraCharges += SubTotal;
    console.log(TotalExtraCharges + "  TotalExtraChargesTotalExtraChargesTotalExtraCharges");
     
    $('.TotalCharges').html('$ <span class="TC">' + TotalExtraCharges + "</span>");
    $("#TotalChargesInput").val(TotalExtraCharges);
    $('#EstimatedTotal').val(TotalExtraCharges);
    GetFilesList();
    
    }

function GetFilesList() {
  $("#InstantQuote tbody").empty();
  var FilesNames = "";
  var FileChargesVar = "";
  var NewPathArray =   [];
$(".DMFileName strong").each(function(){

 FilesNames = ($(this).text());
 FileChargesVar = $(this).parent().siblings(".FileCharges").children('.fileChargesAmt').text()
 
$("#InstantQuote tbody").append(`<tr><td data-toggle="tooltip" title="${FilesNames}">"${FilesNames}"</td><td style='text-align: right;'>$ <span class='Project_charges'>"${FileChargesVar}"</span></td></tr>`)
var fileNamesIncluded = file_paths.filter(element => element.includes(FilesNames));;
fileNamesIncluded = fileNamesIncluded[0];

NewPathArray.push(fileNamesIncluded);

// $("#filePaths").val(fileNamesIncluded);
});

$("#filePaths").val(JSON.stringify(NewPathArray));

}
$(document).on("click", ".ContinueTranscribe", function () {
  var jobid = $("#ConfimationText span").attr("job_id");
  ConfirmTranscibing(jobid);
});

$(document).on("click", ".CancelTranscribe", function () {
  $("#files").empty();
});
$(document).on("click", ".checkoutButton", function () {
  if (validateStep0() == false) {
    isStepValid = false;
    ShowNoty(
      "Please correct the errors before checkout",
      "error"
    );
  } else {
    isStepValid = true;
    $(".sw-btn-next").removeClass("disabled");
    $(".sw-btn-next").trigger("click");
  }



});

function ConfirmTranscibing(jobid) {
  let jobnumber = new FormData();

  jobnumber.append("job_id", jobid);
  if (jobnumber != undefined) {
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
  } else {
    ShowNoty("Something Went Wrong!", "error");
  }
}
function OSConfirmTranscibing(data, success) {
  if (data.status == true) {
    $("#ConfimationModal").modal("hide");
    ShowNoty("File Uploaded successfully!", "alert");
  } else {
    $("#ConfimationModal").modal("hide");
    ShowNoty(data.errors, "alert");
  }
}

function onError() {
  ShowNoty("Something Went Wrong!", "error");
  return false;
}

var pubkey = "";
$(function () {
  $.ajax({
    type: "GET",
    url: "/stripe_payments/get_pub_key/",
    dataType: "json",
    success: function (response) {
      if (response.status) {
        pubkey = response.pub_key;
        OSPubKey();
      } else {
        ShowNoty("Request status is not true", "error");
      }
    },
    error: function (xhr, textStatus) {
      ShowNoty("Something Went Wrong!", "error");
    },
  });
});
function OSPubKey() {
  console.log("Stripe");
  var stripe = Stripe(pubkey);
  var elements = stripe.elements();
  var card = elements.create("card", {
    hidePostalCode: true,
    style: {
      base: {
        iconColor: "#666EE8",
        color: "#31325F",
        lineHeight: "40px",
        fontWeight: 300,
        fontFamily: "Helvetica Neue",
        fontSize: "15px",

        "::placeholder": {
          color: "#CFD7E0",
        },
      },
    },
  });

  if($("#card-element").length > 0){
    card.mount("#card-element");
  }
 

  function setOutcome(result) {
    //  var successElement = document.querySelector('.success');
    var errorElement = document.querySelector(".error");
    //  successElement.classList.remove('visible');
    errorElement.classList.remove("visible");

    if (result.token) {
      // In this example, we're simply displaying the token
      successElement.querySelector(".token").textContent = result.token.id;
      successElement.classList.add("visible");

      // In a real integration, you'd submit the form with the token to your backend server
      //var form = document.querySelector('form');
      //form.querySelector('input[name="token"]').setAttribute('value', result.token.id);
      //form.submit();
    } else if (result.error) {
      errorElement.textContent = result.error.message;
      errorElement.classList.add("visible");
    }
  }

  card.on("change", function (event) {
    setOutcome(event);
  });
document.querySelector("form").addEventListener("submit", function (e) {
    
    e.preventDefault();
    
    $("#submit_payment").addClass("loading");
 $(".stripe-btn.loading").html('<span class="spinner-border spinner-border-sm me-3" role="status" aria-hidden="true"></span>Please wait...');
$(".stripe-btn").attr('disabled','disabled');
    if($("#card-element").length > 0){
    var options = {
      name:
        document.getElementById("first-name").value +
        " " +
        document.getElementById("last-name").value,
      address_line1: document.getElementById("address-line1").value,
      address_line2: document.getElementById("address-line2").value,
      address_city: document.getElementById("city").value,
      address_state: document.getElementById("state").value,
      address_zip: document.getElementById("zip").value,
      address_country: document.getElementById("country").value,
    };
    var EmailID = $("#UserEmail").val();
   
    stripe.createToken(card, options).then(function (result) {
      console.log(result.token);

     
     
      if (result.error) {
        // Inform the user if there was an error.
        // var errorElement = document.getElementById('card-errors');
        // errorElement.textContent = result.error.message;
        console.log("Token Error", result.error);
        ShowNoty(result.error.message, "error");
        
        $("#submit_payment").removeAttr("disabled").removeClass("loading");
        // trackUserAction(EmailID,JSON.stringify(result.error),result.error.message);
         $(".stripe-btn").html('<i class="fa fa-lock me-3"></i>Pay');
$(".stripe-btn").removeAttr("disabled");
      } 
      else {
        console.log("Token ", result.token);

        $("#token").val(result.token.id);
       
        $(".error").hide();
       
        // trackUserAction(EmailID,"token_generated","token_generated");
        //  sendToken();
        var services = {};
        $(".ServiceTypeInput").each(function(){
          var SvcName = $(this).attr("name"); // This is the jquery object of the input, do what you will
          var SvcChg = $(this).attr("value"); // This is the jquery object of the input, do what you will
         
          
          services[SvcName] = SvcChg;
       
    
         });
         services = JSON.stringify(services);
         $("#ProjectDetails").append("<input type='hidden' name='services' value='"+services+"' />")
        let FormSignUp = $("#ProjectDetails").serializeArray();
        console.log(FormSignUp);
    

        $.ajax({
          type: "POST",
          url: "/stripe_payments/create_project/",
          data: FormSignUp, // changed

          success: function (response) {
            console.log("save_payment_method response", response);
            if (response.status) {
              ShowNoty("Payment Successful!", "alert");

              
              $('#smartwizard').smartWizard("stepState", [2], "enable");
              $(".sw-btn-next").removeClass("disabled");
             
              $(".sw-btn-next").trigger("click");
              $("#submit_payment").removeAttr("disabled").removeClass("loading");
              $("#submit_payment").attr('disabled','disabled');
              // ShowNoty(response.message, "alert");
              //  window.location.href = "/user_management/main_dashboard/";
              $('#smartwizard').smartWizard("stepState", [0,1], "");
              $(".sw-btn-prev").addClass("disabled");
             
            } else {
              
              ShowNoty(response.errors, "error");
              $("#submit_payment").removeAttr("disabled").removeClass("loading");
              // window.location.reload();
              $(".stripe-btn").html('<i class="fa fa-lock me-3"></i>Pay');

            }
          },
          error: function (error) {
            ShowNoty(error, "error");
           
          },
          complete: function () {},
        });
        return false; // avoid to execute the actual form submission.
      }
    });
  }
  else {
    var services = {};
        $(".ServiceTypeInput").each(function(){
          var SvcName = $(this).attr("name"); // This is the jquery object of the input, do what you will
          var SvcChg = $(this).attr("value"); // This is the jquery object of the input, do what you will
         
          
          services[SvcName] = SvcChg;
       
    
         });
         services = JSON.stringify(services);
         $("#ProjectDetails").append("<input type='hidden' name='services' value='"+services+"' />")

    let FormSignUp = $("#ProjectDetails").serializeArray();
    console.log(FormSignUp);

    $("#submit_payment").addClass("loading");
    $.ajax({
      type: "POST",
      url: "/stripe_payments/create_project/",
      data: FormSignUp, // changed

      success: function (response) {
        console.log("save_payment_method response", response);
        // $(".stripe-btn").html('<i class="fa fa-lock me-3"></i>Pay');
       
        if (response.status) {
          ShowNoty("Payment Successful!", "alert");
          $('#smartwizard').smartWizard("stepState", [2], "enable");
          $(".sw-btn-next").removeClass("disabled");
      
          $(".sw-btn-next").trigger("click");
          $("#submit_payment").removeAttr("disabled").removeClass("loading");
          $("#submit_payment").attr('disabled','disabled');
          // ShowNoty(response.message, "alert");
          //  window.location.href = "/user_management/main_dashboard/";
          $('#smartwizard').smartWizard("stepState", [0,1], "");
          $(".sw-btn-prev").addClass("disabled");
        } else {
          
          ShowNoty(response.errors, "error");
          $("#submit_payment").removeAttr("disabled").removeClass("loading");
          // window.location.reload();
          $(".stripe-btn").html('<i class="fa fa-lock me-3"></i>Pay');
    
        }
      },
      error: function (error) {
        ShowNoty(error, "error");
      },
      complete: function () {},
    });
    return false; // avoid to execute the actual form submission.
  }
  });

  // trackuser action
  function trackUserAction(EmailID, log, remarks) {
    let error_formdata = new FormData();
    // error_formdata.append("payment-form",payment-form);
    error_formdata.append("UserEmail", EmailID);
    error_formdata.append("error_log", log);
    error_formdata.append("remarks", remarks);
    $.ajax({
      url: "/stripe_payments/create_pay_method_error_log/",
      method: "POST",
      data: error_formdata,
      processData: false,
      contentType: false,
      enctype: "multipart/form-data",
      success: function (response) {
        // console.log(response);
        // $(this).formValid();
        if (response.status) {
          console.log("log saved");
        } else {
        }
      },
      error: function (error) {
        ShowNoty("Something Went Wrong!", "error");
      },
      complete: function () {},
    });
  }

  // $(document).on('click', '#submit', function (e) {
  function sendToken() {
    // e.preventDefault();
    let form = $("#payment-form")[0];
    let formData = new FormData(form);

    // var errorFlag = check_required_validation('invoice-form');
    // if (!errorFlag) {
    // let token = $('#token').val();
    // let token = $('#token').val();
    if (token) {
      $.ajax({
        url: "/stripe_payments/save_payment_method/",
        method: "POST",
        data: formData,
        processData: false,
        contentType: false,
        enctype: "multipart/form-data",
        success: function (response) {
          console.log("save_payment_method response", response);
          if (response.status) {
            ShowNoty(response.message, "alert");
            window.location.href = "/user_management/main_dashboard/";
          } else {
            ShowNoty(response.errors, "error");
            // $("#submit_payment").removeClass("loading").removeAttr('disabled');
            // window.location.reload();
          }
        },
        error: function (error) {
          ShowNoty(error, "error");
        
        },
        complete: function () {},
      });
    } else {
      ShowNoty("Verify card details first", "error");
    }
    // }
  }

  // coutry
  $.ajax({
    type: "GET",
    url: `/user_management/get_countries/`,
    dataType: "json",
    success: function (response) {
      if (response.status) {
        $("#country").html("<option>Select country</option>");
        response.data.forEach((element) => {
          let country_code = element[0];

          $("#country").append(
            "<option value=" +
              country_code +
              ' style="color:#333">' +
              element[1] +
              "</option>"
          );
        });
      } else {
        console.log("request status is not true");
      }
    },
    error: function (xhr, textStatus) {
      alert("error..");
    },
  });


  //country change
  $("#country").on("change", function () {
    console.log("working");
    let id = $(this).val();
    console.log("id", id);
    $.ajax({
      url: "/user_management/get_country_states/?country_id=" + id,
      method: "GET",
      success: function (response) {
        if (response.status === "SUCCESS") {
          let options = `<option value="">Please Select</option>`;
          response.states.forEach((states) => {
            options += "<option value=" + states + ">" + states + "</option>";
          });
          options += `<option value="N/A">Other</option>`;
          $("#state").html(options);
        } else {
        }
      },
      error: function (error) {
        ShowNoty(error, "error");
      },
      complete: function () {},
    });
  });
// payment configurd statua

  $(document).on("click",'#submitLogin', function () {
    var formdata = {
     email: $('#UserEmail').val(),
     password: $('#Signup_password').val(),

    }

    $.ajax({
      url: "/custom_auth/get_payment_info/",
      method: "POST",
      data:formdata,
      success: function (response) {
        // console.log('payment',response)
        if(response.status != true){
          ShowNoty(response.errors, 'error');
        }else{
         
          if (response.payment_configured != true) {
            $('.hideloginRow').addClass('d-none')
            $('.tab-content').css('height','auto');
            
             $('#hidePyement').removeClass('d-none');
             ShowNoty("login Successful!", "success text-white");
             $("#submit_payment").removeAttr('disabled');
           

           } else {
             $('.hideloginRow').addClass('d-none')
            ShowNoty("login Successful!", "success text-white");
             $("#submit_payment").removeAttr('disabled');


             $('.removepeyment').remove();
   
           //   $('#hidePyement').addClass('d-none');
           //  $('#paymentBtn').removeClass('d-none');
   
   
           }
        }
       
      },
      error: function (error) {
        ShowNoty(error, "error");
      },
      complete: function () {},
    });
  });
}

// $('#changeForm').on('click',function(){
  
//  $('input[name="first_name"]').addClass('disabled');
//  $('input[name="last_name"]').addClass('disabled');
//  $('input[name="company"]').addClass('disabled');
//  $('input[name="phone_numberold"]').addClass('disabled');
// $('.D').addClass('d-none');
// $('#register').val('true')


// })

$('#changeForm').on('click',function(){
 
 $('input[name="first_name"]').addClass('disabled').prop('required',false);
 $('input[name="last_name"]').addClass('disabled').prop('required',false);
 $('input[name="company"]').addClass('disabled').prop('required',false);
 $('input[name="phone_numberold"]').addClass('disabled').prop('required',false);
$('.hideRow').addClass('d-none');
$('#backtoRegister').removeClass('d-none');
$('#changeForm').addClass('d-none');
$('#register').val('true');
$('.loginbtn').removeClass('d-none');
$('#hidePyement').addClass('d-none');
$("#submit_payment").attr('disabled','disabled');

});
$(document).on('click','#backtoRegister',function(){
  
  $('input[name="first_name"]').removeClass('disabled');
  $('input[name="last_name"]').removeClass('disabled');
  $('input[name="company"]').removeClass('disabled');
  $('input[name="phone_numberold"]').removeClass('disabled');
 $('.hideRow').removeClass('d-none');
 $('#backtoRegister').addClass('d-none');
 $('#changeForm').removeClass('d-none');
$('.loginbtn').addClass('d-none');
$('#register').val('false');
 $('#hidePyement').removeClass('d-none');

 });

 $(document).on('keyup keypress', 'input', function(e) {
  if(e.which == 13) {
    e.preventDefault();
    return false;
  }else{
    $('#submit_payment').on('click',function(e){
      // formValid();
    });
  
  }
  
});
 
//  formValid = () => {
//   var email = $('input[name="email"]').val();
//   var pwd = $('input[name="password"]').val();
//   var f_name = $('input[name="first_name"]').val();
//   var l_name = $('input[name="last_name"]').val();
//   var C_name = $('input[name="company"]').val();

//   var address_line1 = $('input[name="address_line1"]').val();
//   var address_line2 = $('input[name="address_line2"]').val();
//   var fname = $('input[name="first-name"]').val();
//   var lname = $('input[name="last-name"]').val();
//   var country = $('select[name="country"]').val();
//   var city = $('select[name="city"]').val();
//   var state = $('select[name="state"]').val();
//   var zip = $('input[name="zip"]').val();


// if(email === '' || pwd === '' || f_name === '' || l_name === '' || C_name === '' || address_line1 === '' || address_line2 === '' || fname === '' || lname === '' || country === '' || city === '' || state === '' || zip === ''){
//   ShowNoty('Please fillout the empty field','error');

// }

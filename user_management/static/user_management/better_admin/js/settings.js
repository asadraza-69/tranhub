var CardAddressValues ="";
var card ="";
$(document).ready(function () {
 
    $("#phone_numberold").on("change paste keyup", function () {
      let value = $(this).val();
      $("#phone_number").attr("value", value);
      $("#phone_number").val(value);
    });

    GetUserDetails();
   
   
});


function openSetting(evt, cityName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(cityName).style.display = "block";
    evt.currentTarget.className += " active";
}


document.getElementById("defaultOpen").click();

function GetUserDetails(){
  
    $.ajax({
      type: "GET",
      url: "/user_management/get_user_details/",
      dataType: "json",
      success: function (response) {
        console.log('res',response)
        if (response) {
            $("#UserEmail").val(response.email);
            $("#first_name").val(response.first_name);
            $("#last_name").val(response.last_name);
            $("#company_name").val(response.company);
            var UserEmail = $("#UserEmail").val();
            if (!UserEmail && UserEmail.length <= 0) {
              isValid = false;
              $(".msg-UserEmail").html("Please enter email address").show();
            } else {
              isValid = true;    
              $(".msg-UserEmail").html("").hide();
            } 
            var code = response.phone_number; // Assigning value from model.
         
            $('#phone_numberold').val(code);
            $('#phone_number').val(code);
           
            $('#phone_numberold').prop('readonly', true);

// stripe details
            $("#first-name").val(response.firstname);
            $("#last-name").val(response.lastname);
            $(".Last4Dgts").text(response.last4);
            $(".ExpMM").text(response.exp_month);
            $(".ExpYY").text(response.exp_year);
            if(response.address!= undefined){
                CardAddressValues = response.address 
                $("#address-line1").val(response.address.line1);
                $("#address-line2").val(response.address.line2);                     
                $("#city").val(CardAddressValues.city);
                $("#zip").val(CardAddressValues.postal_code);
            }
            if(response.firstname ==undefined && response.firstname == undefined){
              $("#PaymentType").text("Add");
              $(".EditPaymentDetails").hide();
              $(".DeletePaymentDetails").hide();
              $('#submit_payment,#country,#state ').prop('disabled',false);
    
              $('#first-name,#last-name,#address-line1,#address-line2,#city,#zip').prop('readonly', false);
              $('#submit_payment,#country,#state ').prop('disabled',false);
    $(".card-elementSticker").hide();
    $("#card-element").show();
    
   
    
    
              }
              else{
                $("#PaymentType").text("Update");
                $(".EditPaymentDetails").show();
                $(".DeletePaymentDetails").show();
                $(".card-elementSticker").show();
                $("#card-element").hide();
                $('#first-name,#last-name,#address-line1,#address-line2,#city,#zip').prop('readonly', true);
                $('#submit_payment,#country,#state ').prop('disabled',true);
              }

        } else {
          ShowNoty("Request status is not true", "error");
        }
      },
      error: function (xhr, textStatus) {
        ShowNoty("Something Went Wrong!", "error");
      },
    });


         
  }


function GetCardDetails(){
    $.ajax({
      type: "GET",
      url: "/user_management/get_user_details/",
      dataType: "json",
      success: function (response) {
        console.log('card',response)
        if (response) {
            $("#first-name").val(response.firstname);
            $("#last-name").val(response.lastname);
           $(".Last4Dgts").text(response.last4);
           $(".ExpMM").text(response.exp_month);
           $(".ExpYY").text(response.exp_year);
            if(response.address!= undefined){
                CardAddressValues = response.address 
                $("#address-line1").val(response.address.line1);
                $("#address-line2").val(response.address.line2);                     
                $("#city").val(response.address.city);
                $("#zip").val(response.address.postal_code);
                $("#country").val(response.address.country);
            }
            else{
                $("#address-line1").val("");
                $("#address-line2").val("");                     
                $("#city").val("");
                $("#zip").val("");
                $("#country").val("");
            }
        $("#country").trigger("change");
        if(response.firstname ==undefined && response.firstname == undefined){
          $("#PaymentType").text("Add");
          $(".EditPaymentDetails").hide();
          $(".DeletePaymentDetails").hide();
          $(".card-elementSticker").hide();
           $("#card-element").show();


           if($("#card-element").length > 0 && card != ''){
           
            card.clear();
            // card.mount("#card-element");
          }


          $('#submit_payment,#country,#state ').prop('disabled',false);

          $('#first-name,#last-name,#address-line1,#address-line2,#city,#zip').prop('readonly', false);
          $('#submit_payment,#country,#state ').prop('disabled',false);


          }
          else{
            $("#PaymentType").text("Update");
            $(".EditPaymentDetails").show();
            $(".DeletePaymentDetails").show();
            $(".card-elementSticker").show();
            $("#card-element").hide();
            $('#first-name,#last-name,#address-line1,#address-line2,#city,#zip').prop('readonly', true);
            $('#submit_payment,#country,#state ').prop('disabled',true);
          }
          
        } else {
          ShowNoty("Request status is not true", "error");
        }
      },
      error: function (xhr, textStatus) {
        ShowNoty("Something Went Wrong!", "error");
      },
    });


  }

  function DeleteCardDetails(){
    $.ajax({
      type: "GET",
      url: "/stripe_payments/delete_payment_method/",
      dataType: "json",
      success: function (response) {
        if (response.status) {
            CardAddressValues ="";
            GetCardDetails();
            // window.location.href=window.location.href;
          
           
        } else {
          ShowNoty("Unable to delete, Please try again!", "error");
        }
      },
      error: function (xhr, textStatus) {
        ShowNoty("Something Went Wrong!", "error");
      },
    });


  }
  
    $("#SignUpForm").submit(function(event){
    event.preventDefault();
    var dataString = $("#SignUpForm").serialize();
    $.ajax({
      type: "Post",
      url: "/user_management/edit_user_profile/",
      dataType: "json",
      data: dataString,
      success: function (response) {
        if (response.status) {
           console.log(response);
           ShowNoty("Update successful!", "alert");
           $('.CancelUserDetails').prop('disabled',true);
           $('#first_name,#last_name,#company_name,#phone_numberold').prop('readonly', true);
           $('.SaveUserDetails').prop('disabled',true);
        } else {
          ShowNoty(response.errors, "error");
        }
      },
      error: function (xhr, textStatus) {
        ShowNoty("Something Went Wrong!", "error");
      },
    });

    event.preventDefault();
  });

 
  $('.EditUserDetails').click(function(){
    $('#first_name,#last_name,#company_name,#phone_numberold').prop('readonly', false);
    $('.SaveUserDetails').prop('disabled',false);
    $('.CancelUserDetails').prop('disabled',false);

});
$('.CancelUserDetails').click(function(){
    GetUserDetails();
    $('#first_name,#last_name,#company_name,#phone_numberold').prop('readonly', true);
    $('.SaveUserDetails').prop('disabled',true);
    $('.CancelUserDetails').prop('disabled',true);
});
$('.EditPaymentDetails').click(function(){
     $('#first-name,#last-name,#address-line1,#address-line2,#city,#zip').prop('readonly', false);
    $('#submit_payment,#country,#state ').prop('disabled',false);
    $("#card-element").show();
    $(".card-elementSticker").hide();
    $('.CancelPaymentDetails').prop('disabled',false);
});
$('.CancelPaymentDetails').click(function(){
    GetCardDetails();
    $('.CancelPaymentDetails').prop('disabled',true);
  //   $('#first-name,#last-name,#address-line1,#address-line2,#city,#zip').prop('readonly', true);
  //  $('#submit_payment,#country,#state ').prop('disabled',true);
  //  $("#card-element").hide();
  //  $(".card-elementSticker").show();
});

$('.DeletePaymentDetails').click(function(){

  Swal.fire({
    title: 'Are you sure you want to delete saved payment method?',
    // showDenyButton: true,
    showCancelButton: true,
    confirmButtonText: 'Delete',
    // denyButtonText: `Don't save`,
  }).then((result) => {
    /* Read more about isConfirmed, isDenied below */
    if (result.isConfirmed) {
      Swal.fire('Delete', '', 'success');
      DeleteCardDetails();
    } 
  })
    // if(confirm("Are you sure you want to delete saved payment method?")){
    //     DeleteCardDetails();
    // }
    // else{
    //     return false;
    // }
    
});

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

  $("#SaveCardDetails").click(function () {
    if ($(this).prop("checked")) {
      $(this).val("true");
    } else {
      $(this).val("false");
    }
  });


});

function OSPubKey() {
  console.log("Stripe");
  var stripe = Stripe(pubkey);
  var elements = stripe.elements();
 card = elements.create("card", {
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
//   $("#submit_payment").click(function () {
//     $("#Payment_update").submit();
//   });
  document.querySelector("#submit_payment").addEventListener("click", function (e) {
    e.preventDefault();
    $("#Payment_update").validate();
   if($("#Payment_update").valid()){  
       
    
    
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
   console.log(options);
    stripe.createToken(card, options).then(function (result) {
      console.log(result.token);

     
     
      if (result.error) {
        // Inform the user if there was an error.
        // var errorElement = document.getElementById('card-errors');
        // errorElement.textContent = result.error.message;
        console.log("Token Error strp", result.error);
        ShowNoty(result.error.message, "error");
        
        $("#submit_payment").removeAttr("disabled").removeClass("loading");
        // trackUserAction(EmailID,JSON.stringify(result.error),result.error.message);
         $(".stripe-btn").html('<i class="fa fa-lock"></i> <span id="PaymentType">Update</span> Payment Details');
$(".stripe-btn").removeAttr("disabled");
      } 
      else {
        console.log("Token ", result.token);

        $("#token").val(result.token.id);
       
        $(".error").hide();
       
        // trackUserAction(EmailID,"token_generated","token_generated");
        //  sendToken();
       
       
        let Payment_update = $("#Payment_update").serializeArray();
        console.log(Payment_update);
        $.ajax({
          type: "POST",
          url: "/stripe_payments/edit_payment_method/",
          data: Payment_update, // changed

          success: function (response) {
            console.log("save_payment_method response", response);
            if (response.status) {
              ShowNoty("Payment method saved successfully!", "alert");
           $('.CancelPaymentDetails').prop('disabled',true);


              
            
              $("#submit_payment").removeAttr("disabled").removeClass("loading");
              // trackUserAction(EmailID,JSON.stringify(result.error),result.error.message);
               $(".stripe-btn").html('<i class="fa fa-lock"></i> <span id="PaymentType">Update</span> Payment Details');
      $(".stripe-btn").removeAttr("disabled");
      GetCardDetails();
      $(".card-elementSticker").show();
      $('#first-name,#last-name,#address-line1,#address-line2,#city,#zip').prop('readonly', true);
      $('#submit_payment,#country,#state ').prop('disabled',true);
      $(".ElementsApp .InputElement").val("");
             
            } else {
              
              ShowNoty(response.errors, "error");
              $("#submit_payment").removeAttr("disabled").removeClass("loading");
              // window.location.reload();
              $(".stripe-btn").html('<i class="fa fa-lock"></i> <span id="PaymentType">Update</span> Payment Details');

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
      url: "/stripe_payments/edit_payment_method/",
      data: FormSignUp, // changed

      success: function (response) {
        console.log("save_payment_method response", response);
        // $(".stripe-btn").html('<i class="fa fa-lock"></i> Update Payment Details');
       
        if (response.status) {
            ShowNoty("Payment method saved successfully!", "alert");
        
            $("#submit_payment").removeAttr("disabled").removeClass("loading");
            // trackUserAction(EmailID,JSON.stringify(result.error),result.error.message);
             $(".stripe-btn").html('<i class="fa fa-lock"></i> <span id="PaymentType">Update</span> Payment Details');
    $(".stripe-btn").removeAttr("disabled");
    GetCardDetails();
    $(".card-elementSticker").show();
    $('#first-name,#last-name,#address-line1,#address-line2,#city,#zip').prop('readonly', true);
    $('#submit_payment,#country,#state ').prop('disabled',true);
    $(".ElementsApp .InputElement").val("");
        } else {
          
          ShowNoty(response.errors, "error");
          $("#submit_payment").removeAttr("disabled").removeClass("loading");
          // window.location.reload();
          $(".stripe-btn").html('<i class="fa fa-lock"></i> <span id="PaymentType">Update</span> Payment Details');
    
        }
      },
      error: function (error) {
        ShowNoty(error, "error");
      },
      complete: function () {},
    });
    return false; // avoid to execute the actual form submission.
  }


  
}
else{
    ShowNoty("Invalid Details", "error");
}
  });


  // $(document).on('click', '#submit', function (e) {


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
        $("#country").val(CardAddressValues.country);
        $("#country").trigger("change");
      
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
      complete: function () {
        $("#state").val(CardAddressValues.state);
      },
    });
  });
}

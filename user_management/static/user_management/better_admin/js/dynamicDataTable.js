var mainPageTitle = ''
var true_values = [ 'yes', 'active', 'no lock', 'normal' ]
var false_values = ['no', 'inactive', 'locked', 'bar all calls' ]
var info_values = ['info']

function getAndRenderDynamicTable (url, table_id, tableParentDiv = '#tableApp') {
    dynamicTable_url = url
    dynamicTable_id = table_id
    tableDiv = $(tableParentDiv)

    $.ajax({
        url:url,
        method: "GET",
        success: function (response) {
            // var response = {"page_lis_title": "FeeGroup", "headers": ["", "Group Name", "Classes", "Late Fees", "Template", "Fee Types", "Bank", "Course Assigned", "Custom", "Status", "Action"], "page_title": "Fee Group", "data": [[["", ""], ["group 1", "35"], [[["bits-g - bscs > 2 semester", 26]], ["modal", "section"]], ["Default", ""], ["Default", ""], [[["security deposit", ""], ["admission fees", ""], ["lab fees", ""], ["tuition fees", ""]], ["modal", "Feetype"], [{"timetable": false}]], ["Faysal Bank", ""], ["False", ""], ["False", ""], ["True", ""], [[["/fms/create_update_feegroup/?id=35", "Edit", ""], [35, "Generate Voucher", "edit"]], "action"]], [["", ""], ["Applied Physics-Semester 2", "37"], [[["bits-g - applied physics > 2 semester", 30]], ["modal", "section"]], ["After 15 days", ""], ["Default", ""], [[["security deposit", ""], ["lab fees", ""], ["tuition fees", ""]], ["modal", "Feetype"], [{"timetable": false}]], ["Meezan Bank", ""], ["False", ""], ["False", ""], ["True", ""], [[["/fms/create_update_feegroup/?id=37", "Edit", ""], [37, "Generate Voucher", "edit"]], "action"]], [["", ""], ["default custom group", "36"], [[], ["modal", "section"]], ["After 15 days", ""], ["Default", ""], [[], ["modal", "Feetype"], [{"timetable": false}]], ["Faysal Bank", ""], ["False", ""], ["True", ""], ["True", ""], [[["/fms/create_update_feegroup/?id=36", "Edit", ""]], "action"]], [["", ""], ["G1", "38"], [[["bits-g - XI - Ninth > XI - A", 57]], ["modal", "section"]], ["After 15 days", ""], ["Default", ""], [[["admission fees", ""], ["lab fees", ""], ["tuition fees", ""]], ["modal", "Feetype"], [{"timetable": false}]], ["Faysal Bank", ""], ["False", ""], ["False", ""], ["True", ""], [[["/fms/create_update_feegroup/?id=38", "Edit", ""], [38, "Generate Voucher", "edit"]], "action"]], [["", ""], ["Bs(CS) Semester 1", "40"], [[["bits-g - bscs > 1 semester", 25]], ["modal", "section"]], ["After 15 days", ""], ["Default", ""], [[["security deposit", ""], ["lab fees", ""], ["tuition fees", ""]], ["modal", "Feetype"], [{"timetable": false}]], ["Faysal Bank", ""], ["False", ""], ["False", ""], ["True", ""], [[["/fms/create_update_feegroup/?id=40", "Edit", ""], [40, "Generate Voucher", "edit"]], "action"]], [["", ""], ["Secondary", "39"], [[["bits-g - bsse > 2 semester", 28], ["bits-g - applied physics > 1 semester", 29]], ["modal", "section"]], ["After 15 days", ""], ["Default", ""], [[["lab fees", ""], ["tuition fees", ""]], ["modal", "Feetype"], [{"timetable": false}]], ["Faysal Bank", ""], ["False", ""], ["False", ""], ["True", ""], [[["/fms/create_update_feegroup/?id=39", "Edit", ""], [39, "Generate Voucher", "edit"]], "action"]], [["", ""], ["Secondary1", "44"], [[["bits-n - SCI 1 > SCI SEC 1", 51]], ["modal", "section"]], ["After 15 days", ""], ["Default", ""], [[["lab fees", ""], ["tuition fees", ""]], ["modal", "Feetype"], [{"timetable": false}]], ["Faysal Bank", ""], ["False", ""], ["False", ""], ["True", ""], [[["/fms/create_update_feegroup/?id=44", "Edit", ""], [44, "Generate Voucher", "edit"]], "action"]]], "model_name": "FeeGroup"}
            renderDynamicTable(response, table_id);

        },
        error: function(error){
            $('.spinner.loading').remove();
            tableDiv.html('<h5> <strong> Sorry </strong> <span> No Data Found ! </span> </h5>');

        }
    });
}

function renderDynamicTable(response, table_id, extras = true, tableDiv = $('#tableApp')) {
        if(response.app_label) {
        var appName = response.app_label
    }else {
        var appName = urlParse()[1]
    }if(response.button_title){
        var buttonTitle = response.button_title;
    }
    else if(response.page_list_title) {

        var buttonTitle = response.page_list_title.split(' ')[0]
        mainPageTitle = buttonTitle
    }
    var table_app_html;
    if(extras) {
        table_app_html = ''+
        '<div class="breadcrums">'+
            '<ul id="page_breadcrums"></ul>'+
        '</div>'+

        '<div class="page_header">'+
            '<h2>'+
                '<span id="pageTitle"></span>'+
                '<small id="pageListTitle"></small>'+
            '</h1>'+
                '<button class="btn btn-sm btn-secondary searchBarToggle float-end mx-1" data-bs-toggle="tooltip" data-bs-placement="top" title="Advance table options" data-position="left center" data-id="'+table_id+'"><i class="fa fa-sliders" aria-hidden="true"></i></button>'+
                '<button class="btn btn-sm btn-secondary labeled modelFormTrigger float-end" data-name="'+buttonTitle+'" data-model_name="'+response.model_name+'" data-app_name="'+appName+'"  data-status="create"><i class="fa fa-plus-square" aria-hidden="true"></i> Create '+buttonTitle+'</button>'+
        '</div>'+

        '<div class="table-container ui form mini list_viewTable_container">'+
            '<table id="'+table_id+'" class="table list_viewTable table-sm table-bordered ba-table"></table>'+
        '</div>'
    } else {
        table_app_html = ''+
            '<div class="table-container ui form mini list_viewTable_container">'+
                '<table id="'+table_id+'" class="table list_viewTable table-sm table-bordered"></table>'+
            '</div>'
    }
 

   
    tableDiv.html(table_app_html);
    createDynamicDataTable(response.data, response.headers, table_id, appName, response.model_name);

    $('.spinner.loading').remove();
    $('#pageTitle').html(response.page_title)
    $('#pageListTitle').html(response.page_list_title)
    var breadcrumList = response.breadcrums  // Temp List
    if(breadcrumList) {
        var htmlList = ""
        $.each(breadcrumList, function (index, value) {
            if(value[1].length) {
                htmlList += '<li><a href="'+value[1]+'">'+value[0]+'</a></li>'
            }else {
                htmlList += '<li class="breadCrum-nolink"><a>'+value[0]+'</a></li>'
            }
        });
        $('#page_breadcrums').html(htmlList);
    }
}



var oTable = {};
var no_sort=[];
function createDynamicDataTable(data_set, headers, table_id, getAppName, getModelName) {
    this.headers = headers;
    this.data_set = data_set;
    this.table_id = table_id;
    $('#'+table_id).show();
    var headerDict = []
    $.each(headers, function(index, value){
        if (value == "Action") {
            no_sort.push(index);
        }
        headerDict.push({"title": value}) 
    })
    var buttonArray = {"edit":["green","write"],"view":["blue","zoom"],"delete":["red","remove"]}
    var that = this;
    oTable[table_id] = $('#'+this.table_id).DataTable( {
        destroy: true,
        columns: headerDict,
        data: this.data_set,
        deferRender: true,
        "autoWidth": false,
        order: [],
        lengthMenu: [[10, 25, 50, 100, 500, 1000], [10, 25, 50, 100, 500, 1000]],
        columnDefs: [
            // orderable: false, targets: no_sort ,
            { targets: no_sort, orderable: false,width:'50px'},
            { targets: '_all',  orderable: true,
            render: function(data, type, full, meta) {
                return data[0];
            },
            createdCell: function(td, data, rowData, row, col) {
                //   console.log(td.innerHTML);

                $(td).attr("data-id", data[1]);
            },
        } ],
        // columnDefs: [
            
        //     {
        //         'targets': ["_all"],
        //         // render: function (data, type, full, meta){
        //         //     return data[0];
        //         // },
                
        //         "createdCell": function (td, data, rowData, row, col) {
        //             $(td).attr('data-id', data[1]);
        //         }
        //     }
        // ],
        "drawCallback" : function() {
            var api = this.api();
            var apiRowData = api.rows({page:'current'}).data().toArray()
            var tableWidth = $('#'+that.table_id+'').width()    
            var tableAppWidth = tableDiv.width()  
            var wordCountLimit = 34
            var overheadClass = ""


            if(apiRowData.length){
                var columnsCounts = apiRowData[0].length

                if(columnsCounts <= 5) {
                    var overheadClass = 'large'
                    wordCountLimit = 200
                }
                else if(columnsCounts > 8 && wordCountLimit < 11) {
                    var overheadClass = 'small'
                    wordCountLimit = 22
                }else if(columnsCounts > 10){
                    var overheadClass = 'mini'
                    wordCountLimit = 14
                }
            }



            api.rows({page:'current'}).nodes().each(function(tr, index) {
                var $row = $(tr);
                $row.find('td').each(function(idx, elem){
                    var dropdownBtnCount = 0
                    var cellData = api.cell(this).data()
                  
                    $(this).html(cellData[0])

                    if(cellData[0]) {
                        if(website_regex.test(cellData)) {
                            $(this).addClass('no_sentencecase');
                        }
                     
                            
                        if(cellData[1] == "action") {
                            var buttonHtml = ''
                            // var buttonsLength = cellData[0].length
                            var dropdownHtml = ""
                            var dropdownButton="";
                            // dropdownHtml =  '<div class="action_btn_dots ui icon dropdown button white">'+
                            //                     '<i class="fa fa-ellipsis-v" aria-hidden="true"></i>'+
                            //                     '<div class="menu">'+
                            //                     '</div>'+
                            //                 '</div>'
                            dropdownHtml = ' <div class="btn-group">'+
                            ' <a class="px-3" href="#" type="button"  data-bs-toggle="dropdown" aria-expanded="false">'+
                            '  <i class="fa fa-ellipsis-v" aria-hidden="true"></i>'+
                            ' </a>'+
                            '  <ul class="menu dropdown-menu dropdown-menu-end">'+
                           
                            
                            ' </ul>'+
                            ' </div>'

                            var dropdownFlag;
                            var dropdownButton = ""

                            $.each(cellData[0], function(index, button){
                                dropdownFlag = false
                                
                                var buttonUrl = button[0]
                                var buttonTitle = button[1]
                                var buttonAction = button[2]

                                var reUrlPath = /^\/?([^:\/\s]+)(:([^\/]*))?((\/\w+)*\/)([\w\-\.]+[^#?\s]+)(\?([^#]*))?(#(.*))?$/m;
                                if (reUrlPath.test(buttonUrl)) { 
                                    buttonAction = "url"
                                    } 
                                  

                             
                                if(buttonAction == "edit") {
                                  
                                    dropdownButton += '<li><a class="dropdown-item" data-nametrigger="'+mainPageTitle.toLowerCase().replace(/ /g,'_')+'" data-name="'+mainPageTitle+'" data-url="'+buttonUrl+'" data-model_name="'+getModelName+'" data-app_name="'+getAppName+'" data-status="edit" >'+buttonTitle+'</a></li>'
                                }
                                else if (buttonAction == "url"){
                                    dropdownButton += '<li><a href="'+buttonUrl+'" data-id="'+buttonUrl+'" data-action="'+((buttonAction)?buttonAction: buttonTitle.toLowerCase().replace(/ /g,'_'))+'" class="dropdown-item" data-nametrigger="'+mainPageTitle.toLowerCase().replace(/ /g,'_')+'" >'+buttonTitle+'</a></li>'
                                }
                                else {
                                    dropdownButton += '<li><a href="#" data-id="'+buttonUrl+'" data-action="'+((buttonAction)?buttonAction: buttonTitle.toLowerCase().replace(/ /g,'_'))+'" class="dropdown-item" data-nametrigger="'+mainPageTitle.toLowerCase().replace(/ /g,'_')+'">'+buttonTitle+'</a></li>'
                                }

                            });

                            $(this).html(dropdownHtml);
                            $(this).addClass('text-center');
                            // console.log(dropdownButton,"   dropdownButton");
                            $(this).find('.btn-group').find('.dropdown-menu').html(dropdownButton);
                            if(dropdownButton != ""){
                                $(this).find('.btn-group').find('.dropdown-menu').html(dropdownButton);
                            }
                          else{
                            $(this).find('.btn-group a').css('cursor','not-allowed');
                            $(this).find('.btn-group').find('.dropdown-menu').hide();
                          }
                           

                          
                           
                  
                            $(this).width('5');
                        }
                        else if(cellData[1][0] == "modal") {
                            $(this).parents('table').find('thead:first').find('th:eq('+idx+')').addClass('text-center')
                            if(cellData[0].length) {
                                var modalButton_html = '<button class="ui blue circular icon button dynamicTableColumnModal" data-bs-toggle="tooltip" data-bs-placement="top" data-tooltip="'+cellData[1][1].toSentenceCase()+' List" title="'+cellData[1][1].toSentenceCase()+' List" data-inverted="" data-modalname="'+cellData[1][1]+'"> <i class="list icon"></i> </button>'
                            }
                            else {
                                var modalButton_html = '<button class="ui circular icon button" data-bs-toggle="tooltip" data-bs-placement="top" data-tooltip="No '+cellData[1][1].toSentenceCase()+' Found" title="No '+cellData[1][1].toSentenceCase()+' Found" data-inverted="" data-modalname="'+cellData[1][1]+'"> <i class="list icon"></i> </button>'
                            }
                            $(this).addClass('text-center').width('120').html(modalButton_html);
                        }
                        else {
                            
                            var colValue = tooltipVal = cellData[0]
                            // if(moment(cellData[0]).isValid() && isNaN(cellData[0])) {
                            //     var match = cellData[0].indexOf(':')
                            //     if(Date.parse(cellData[0])){
                            //         if (match >= 0) {
                            //             var date_formate = 'MMM dd, yyyy HH:mm:ss'
                            //         }else {
                            //             var date_formate = 'MMM dd, yyyy'
                            //         }
                            //         var tooltip_date_formate = 'MMMM dd, yyyy HH:mm:ss'
                            //         var colValue = Date.parse(cellData[0]).toString(date_formate)
                            //         var tooltipVal = Date.parse(cellData[0]).toString(tooltip_date_formate)
                            //         $(this).html(colValue)
                            //     }
                            // }

                            if(cellData[0].length > wordCountLimit ) {
                                $(this).html('<div data-position="right center" data-inverted=""  data-bs-toggle="tooltip" data-bs-placement="top" data-tooltip="'+tooltipVal+'" title="'+tooltipVal+'"><span class="overhead '+overheadClass+'" >'+colValue+'</span></div>')
                            }

                            if(!isNaN(colValue)) {
                                if(!Number.isInteger(Number(colValue))) {
//                                    colValue = numeral(colValue).format('(0,0.0000000)')
                                    $(this).html(colValue)
                                }
                                
                            }
                            if(isNaN(cellData[0])) {
                                if( $.inArray(cellData[0].toLowerCase() ,true_values) != -1) {
                                    $(this).html('<i class="fa fa-check-circle text-success" aria-hidden="true"></i>').addClass('text-center')
                                    .addClass('text-center')
                                 
                                }
                                if( $.inArray(cellData[0].toLowerCase() ,false_values) != -1) {
                                    $(this).html('<i class="fa fa-times-circle text-danger" aria-hidden="true"></i>').addClass('text-center')
                                    .addClass('text-center')
                                 
                                }
                                if( $.inArray(cellData[0].toLowerCase() ,info_values) != -1) {
                                    $(this)
                                        .html('<i class="fa fa-info-circle text-info" aria-hidden="true"></i>')
                                        .addClass('text-center')
                                        .attr({
                                            "title":cellData[0],
                                            "data-tooltip":cellData[0],
                                            "data-position":"bottom center"
                                        });
                                }
                            }
                        }
                    }
                });
            });
             $('.ui.dropdown').dropdown();
            // $('.inline').popup({
            //     transition: "scale",
            // });
            responsiveTable('body');

        },
        "initComplete": function(settings, json) {
            // Add a text input to each footer cell


            $('#dynamicTableModal').remove();
            var filters_header = '<tr>';
            $(settings.nTHead).find('th').each(function(index, el) {
                filters_header += '<th>'+$(el).text()+'</th>';
            });
            filters_header += '</tr>';
            $(settings.nTHead).parent().find('.'+that.table_id+'_filters').remove();
            $(settings.nTHead).after('<thead class="'+that.table_id+'_filters filters-head hide ui form thead-dark">'+filters_header+'</thead>');

            $('#'+table_id+' .'+table_id+'_filters th').each(function () {
                var title = $(this).text();
                if ( title == 'Action' ) {
                    $(this).html('');
                } else if(title == 'Playback Status' || title == 'Hot Target' || title == 'Is Active' || title == 'User Status') {
                    $(this).html(`<select>
                    <option value="">All</option>
                    <option value="true">Active</option>
                    <option value="false">In Active</option>
                    </select>`);
                }
                else {
                    $(this).html('<div class="form-group mb-0"><input type="text" class="form-control form-control-sm" placeholder="Search in '+title+'" /><span class="ui small loader"></span><i class="fa fa-remove"></i></div>');
                }
            });
            // Add Advance Filter Button

            var advFilterBtn = '<div><a id="'+that.table_id+'_toggle_filter" class="btn btn-sm  btn-secondary "><i class="fa fa-filter" aria-hidden="true"></i></a></div>'
            var searchField = '<div id="'+that.table_id+'_datatable-search-ui"><span id="'+that.table_id+'_input_field_cont" style="display:none;"><input class="animated form-control form-control-sm" id="'+that.table_id+'_search_field" placeholder="Search"></span><a id="'+that.table_id+'_toggle_search" class="btn btn-sm btn-secondary toggle_search mx-1"><i class="fa fa-search" aria-hidden="true"></i></a></div>'

            $(settings.nTableWrapper).find('#'+that.table_id+'_toggle_filter').remove();
            $(settings.nTableWrapper).find('#'+that.table_id+'_filter')
                .html(searchField + advFilterBtn);

            // Add Advance Filter Button Click Function
            $('#'+that.table_id+'_toggle_filter').click(function(event) {
                $('.'+that.table_id+'_filters').toggleClass('hide');
                $('.'+that.table_id+'_filters').find('input').val('');
                oTable[table_id].search('').draw(false)
            });
            $('#'+table_id+'_toggle_search').click(function(){
                $('#'+table_id+'_input_field_cont').show().removeClass('fadeOut').addClass('animated fadeIn');
                $('#'+table_id+'_input_field_cont').find('i.fa-search').animate({
                    left:10,
                },500, function(){
                    $(this).parent().find('input').attr('placeholder', 'Search ...').focus();
                });

            });
            $('#'+table_id+'_input_field_cont').find('input').blur(function(){
                var thisValue = $(this).val();
                if(!thisValue) {
                    $('#'+table_id+'_input_field_cont').find('i.fa-search').removeAttr('style')
                    $('#'+table_id+'_input_field_cont').find('i.fa-search').animate({
                        right:5
                    },500, function(){
                    });
                    // $(this).parent().find('input').removeAttr('placeholder')
                    $('#'+table_id+'_input_field_cont').removeClass('fadeIn').addClass('animated fadeOut').hide();
                }
            });
            $('#'+table_id+'_input_field_cont').find('input').keyup(function(){
                oTable[table_id].search( $(this).val() ).draw(false)
            });



            // dataTables_length
            // dataTables_filter
            var dataId = $('.searchBarToggle').attr('data-id');
            $('#'+dataId+'_filter, #'+dataId+'_length');
            // $('#'+that.table_id+'_filter, #'+that.table_id+'_length').slideUp();
            $('.searchBarToggle').on('click', function () {
                var $this = $(this);
                var dataId = $this.attr('data-id');
                var hasClass = $('#'+dataId+'_filter').hasClass('active');
                if(hasClass) {
                    $('#'+dataId+'_filter, #'+dataId+'_length').removeClass('active')
                }else {
                    $('#'+dataId+'_filter, #'+dataId+'_length').addClass('active');
                }
            });

            var dynamicTableColumnModal_HTML = ''+
                '<div class="ui modal small border_radius" id="dynamicTableModal">'+
                    '<i class="fa fa-remove"></i>'+
                    '<div class="header" id="dynamicTableModal_header"></div>'+
                    '<div class="content">'+
                        '<div class="search_dynamicTableModal_Field">'+
                            '<div class="ui form">'+
                                '<div class="form-group mb-0">'+
                                    '<input type="text" class="form-control form-control-sm" id="search_dynamicTableModal_List_Input" placeholder="">'+
                                '</div>'+
                            '</div>'+
                        '</div>'+
                        '<div class="dynamicTableModal_listContainer">'+
                            '<ul id="dynamicTableModal_ListTag"></ul>'+
                        '</div>'+
                    '</div>'+
                '</div>'

            tableDiv.find('#dynamicTableModal').remove();
            tableDiv.append(dynamicTableColumnModal_HTML);
            
            tableWrapOverlapContainer ()

            $(window).resize(function(){
                tableWrapOverlapContainer ();
            });

            function tableWrapOverlapContainer () {
                var tableWidth = $('#'+that.table_id+'').width()    
                var tableAppWidth = tableDiv.width()+20
                $('.tableOuterOverlap').removeClass('table_overlaping')
                if(tableWidth > tableAppWidth) {
                    if( !$('.tableOuterOverlap').length ) {
                        $('#'+that.table_id+'').wrap('<div class="tableOuterOverlap"></div>');
                    }
                    $('.tableOuterOverlap').addClass('table_overlaping');
                }
            }     
            var tableWidth = $('#'+that.table_id).width;
        }
    });

    // Apply the search
    var timer,
        $searchInput = $('#'+table_id+' input[type=text], #'+table_id+' select'),
        $loaders = $searchInput.parent().find('.ui.loader');

    $searchInput.on('keyup change', function () {
        var $this = $(this),
            thisVal = $this.val(),
            idx = $this.closest('th').index(),
            $loader = $this.parent().find('.ui.loader');
        $loader.addClass('active');
        if ( thisVal ) {
            oTable[table_id]
                .column( idx )
                .search( thisVal )
                .draw();
            $loaders.removeClass('active');
        }
        else {
            oTable[table_id]
                .column( idx )
                .search( '' )
                .draw();
            $loaders.removeClass('active');
        }
    });

    $searchInput.on('keydown change', function () {
        clearTimeout(timer);
    });

    // Clear column filter fields
    $('.fa-remove').click(function(event) {
        $(this).parent().find('input:text').val('');
        $(this).parent().find('input:text').trigger('keyup')
    });

    var $dynamicTableModal = $('#dynamicTableModal');
    tableDiv.off('click').on('click','.dynamicTableColumnModal', function(){
        var $cellNode = $(this).parents('td:first');
        var cellData = oTable[table_id].cell($cellNode).data();
        var listOfValues =  cellData[0]
        var timeTableCheck =  cellData[2]
        var modalName =  cellData[1][1]
        var timeTableToolTip = true
        var dateFormat = 'MMM dd, yyyy'
        if(modalName == "months") {
            dateFormat = 'MMM yyyy'
        }
        if(timeTableCheck){
            console.log('timeTableCheck', timeTableCheck, timeTableCheck[0]["timetable"])
            timeTableToolTip = timeTableCheck[0]["timetable"]
            
        }

        $('#dynamicTableModal_header').html(modalName.toSentenceCase()+' List');

        $('#search_dynamicTableModal_List_Input').attr('placeholder','Search ' +modalName.toSentenceCase()).val('');


        var listOfValues_HTML = ""
        $.each(listOfValues, function(index, value){

            if(timeTableToolTip) {
                console.log('timeTableCheck',timeTableToolTip)
                listOfValues_HTML += '<li data-name="'+value[0].toLowerCase()+'" data-id="'+value[1]+'" data-inverted="" data-bs-toggle="tooltip" data-bs-placement="top" data-tooltip="'+value[0]+'" title="'+value[0]+'"><a>'+value[0]+'</a></li>'
    
                }else {
                var textValue = value[0]
                if(moment(value[0]).isValid() && isNaN(value[0])) {
                    if(Date.parse(value[0])){
                        var colValue = Date.parse(value[0]).toString(dateFormat)
                        textValue = colValue
                    }
                }
                listOfValues_HTML += '<li data-name="'+textValue.toLowerCase()+'" data-id="'+value[1]+'" data-inverted="" ><span title="'+textValue+'">'+textValue+'</span></li>'
            }
        });

        $('#dynamicTableModal_ListTag').html(listOfValues_HTML)
        $dynamicTableModal.modal('show');
    });
    $('body').on('keyup', '#search_dynamicTableModal_List_Input',function(){
        var thisValue = $(this).val();
        if ( thisValue ) {
            $('#dynamicTableModal_ListTag').find('li').hide()
            $('#dynamicTableModal_ListTag').find('li[data-name*="'+thisValue.toLowerCase()+'"]').show()
        }
        else {
            $('#dynamicTableModal_ListTag').find('li').show()
        }
    });
}

var format = 'hh:mm:ss'

function responsiveTable(elem) {
    $(elem).find(".sa-table:not(.no-responsive) tbody tr, .ba-table:not(.no-responsive) tbody tr").each(function () {
        var $firstTd = $(this).find("td:first-child")
        var $secondTd = $(this).find("td:eq(1)");
        var trButtonLenght = $(this).find('span.tr-button').length;
        $(this).find('td').each(function(index, elem){
        
            var classCheck = $(this).hasClass('checkbox_row');
            var title = $(this).parents('table').find('thead th:eq('+index+')').text();
            if(index == 0) {
                if(classCheck) {
                    $(this).parents('table').addClass('responsiveFirstColumn');
                    $(this).attr({
                        "data-responsive":"hide",
                        "data-responsive-hide-title" :"hide"
                    });
                }

            }
            if(classCheck) {
                $(this).attr('data-title', 'Select Row')
            }
            else {

                $(this).attr('data-title', title)
            }
            var $this = $(this),
                thisTxt = $this.html();
            if(thisTxt == "" || thisTxt == "-" || thisTxt == " " || thisTxt == "none" || thisTxt == "None") {
                $this.html('-').removeClass('text-right').addClass('text-center')
            }
            if($this.hasClass('humanizeNum') || title == 'Amount' || title == 'amount') {
                var string = numeral(thisTxt).format('0,0.00')
                $this.html(string)
            }
        })

        if(!trButtonLenght) {
            if($firstTd.attr('data-responsive') == "hide"){
                $secondTd.append("<span class='tr-button'></span>")
            }
            else {
                $firstTd.append("<span class='tr-button'></span>");
            }
        }
    });

    $(elem).find(".sa-table:not(.no-responsive) tbody tr .tr-button, .ba-table:not(.no-responsive) tbody tr .tr-button").off().on("click",function(){
        $(this).toggleClass("open").parent().parent().toggleClass("open");
    });
}

$(function(){
    responsiveTable('.table-container')
})

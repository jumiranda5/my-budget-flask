$(document).ready(function(){

    // Update payed status on checkbox click
    $("input").click(function() {
        var name = $(this).attr("name")
        if (name === "edit-payed") {
            var id = $(this).attr("class")
            var isChecked = $(this).is(":checked")
            $.post("/edit-payed/" + id + "/" + isChecked)
        }
        else if (name == "type") {
            var id = $(this).attr("id")
            if (id === "in") {
                $("#payed-label").text("Received")
            }
            else {
                $("#payed-label").text("Payed")
            }
        }
    });

    // Home page => update month div on prev button click
    $("#prev-month").click(function(){
        
        var year = $("#current-month-year").val()
        var month = $("#current-month").val()
        path = "/balance/" + year + "/" + month + "/prev"

        $.get(path, function(data, status){
            update_month(data)
        });
    })

    // Home page => update month div on next button click
    $("#next-month").click(function(){
        
        var year = $("#current-year").val()
        var month = $("#current-month").val()
        path = "/balance/" + year + "/" + month + "/next"

        $.get(path, function(data, status){
            update_month(data)
        });
    })

    // Update month div
    function update_month(data) {
        
        $("#current-month-year").val(data.date.year)
        $("#current-month").val(data.date.month)
        $("#month-year").text(data.date.year)
        $("#month").text(data.date.month_name)
        $("#month-total").text(data.balance.total)
        $("#month-income").text(data.balance.income)
        $("#month-out").text(data.balance.out)

        var newUrl = "/month/" + data.date.year + "/" + data.date.month 
        $("#month-link").attr("href", newUrl);
    }

    // Home page => update year div on prev button click
    $("#prev-year").click(function(){
        
        var year = $("#current-month-year").val()
        path = "/year-balance/" + year + "/prev"

        $.get(path, function(data, status){
            update_year(data)
        });
    })

    // Home page => update year div on next button click
    $("#next-year").click(function(){
        
        var year = $("#current-year").val()
        path = "/year-balance/" + year + "/next"

        $.get(path, function(data, status){
            update_year(data)
        });
    })

    // Update year div
    function update_year(data) {    
        $("#current-year").val(data.year)
        $("#year").text(data.year)
        $("#year-balance").text(data.balance)

        $(".year-month > p").each(function(i) {
            $(this).text(data.months[i].balance.total);
        });
    }
});

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

        console.log(path)

        $.get(path, function(data, status){
            update_month(data)
        });
    })

    // Home page => update month div on next button click
    $("#next-month").click(function(){
        
        var year = $("#current-month-year").val()
        var month = $("#current-month").val()
        path = "/balance/" + year + "/" + month + "/next"

        console.log(path)

        $.get(path, function(data, status){
            update_month(data)
        });
    })

    // Update month div
    function update_month(data) {
        
        // update html
        $("#current-month-year").val(data.date.year)
        $("#current-month").val(data.date.month)
        $("#month-year").text(data.date.year)
        $("#month").text(data.date.month_name)
        $("#month-income").text(data.balance.income)
        $("#month-out").text(data.balance.out)
        $("#month-total").text(data.balance.total_currency)

        // Change balance color according to value
        if (data.balance.total >= 0) {
            $("#month-total").removeClass("out")
            $("#month-total").addClass("positive")    
        }
        else {
            $("#month-total").addClass("out")
            $("#month-total").removeClass("positive")
        }

        var newUrl = "/month/" + data.date.year + "/" + data.date.month 
        $("#month-link").attr("href", newUrl);
    }

    // Home page => update year div on prev button click
    $("#prev-year").click(function(){
        
        var year = $("#current-year").val()
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
        $("#year-balance").text(data.balance_currency)

        // Change balance color according to value
        if (data.balance >= 0) {
            $("#year-balance").removeClass("out")
            $("#year-balance").addClass("positive")    
        }
        else {
            $("#year-balance").addClass("out")
            $("#year-balance").removeClass("positive")
        }

        // Update each list item
        $(".year-month-balance").each(function(i) {
            
            // Update balance value
            $(this).text(data.months[i].balance.total_currency);
            
            // Change balance color according to value
            if (data.months[i].balance.total >= 0) {
                $(this).removeClass("out")
                $(this).addClass("positive")    
            }
            else {
                $(this).addClass("out")
                $(this).removeClass("positive")
            }

        });
    }
});

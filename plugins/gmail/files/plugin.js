function param_gmail(){
    var xmlhttp = new XMLHttpRequest();
    var theUrl = "/api/gmail/param";
    xmlhttp.open("POST", theUrl);
    var data = new FormData();
    data.append("gmailuser", document.getElementById("gmailuser").value);
    data.append("gmailpassword", document.getElementById("gmailpassword").value);
    data.append("fromagenda", document.getElementById("fromagenda").value);
    xmlhttp.send(data);
}
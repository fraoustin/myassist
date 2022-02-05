function param_gmail(){
    var xmlhttp = new XMLHttpRequest();
    var theUrl = "/api/gmail/param";
    xmlhttp.open("POST", theUrl);
    var data = new FormData();
    data.append("gmailuser", document.getElementById("gmailuser").value);
    data.append("gmailpassword", document.getElementById("gmailpassword").value);
    xmlhttp.send(data);
}

function del_gmail(obj){
    var xmlhttp = new XMLHttpRequest();
    var theUrl = "/api/gmail/del";
    xmlhttp.open("POST", theUrl);
    var data = new FormData();
    data.append("gmail", obj.id);
    xmlhttp.send(data);
    obj.parentNode.parentNode.parentNode.removeChild(obj.parentNode.parentNode);
}

function add_gmail(){
    document.getElementById("addgmail").style.display="";
}

function close_gmail(){
    document.getElementById("addgmail").style.display="none";
}

function save_gmail(){
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            location.reload();
        };
    };
    var theUrl = "/api/gmail/add";
    xmlhttp.open("POST", theUrl);
    var data = new FormData();
    data.append("name", document.getElementById("name").value);
    data.append("url", document.getElementById("url").value);
    xmlhttp.send(data);
    document.getElementById("addgmail").style.display="none";
}
function del_podcast(obj){
    var xmlhttp = new XMLHttpRequest();
    var theUrl = "/api/podcast/del";
    xmlhttp.open("POST", theUrl);
    var data = new FormData();
    data.append("podcast", obj.id);
    xmlhttp.send(data);
    obj.parentNode.parentNode.parentNode.removeChild(obj.parentNode.parentNode);
}

function add_podcast(){
    document.getElementById("addpodcast").style.display="";
}

function close_podcast(){
    document.getElementById("addpodcast").style.display="none";
}

function save_podcast(){
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            location.reload();
        };
    };
    var theUrl = "/api/podcast/add";
    xmlhttp.open("POST", theUrl);
    var data = new FormData();
    data.append("name", document.getElementById("name").value);
    data.append("url", document.getElementById("url").value);
    xmlhttp.send(data);
    document.getElementById("addpodcast").style.display="none";
}
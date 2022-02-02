function htmlToElement(html) {
    var template = document.createElement('template');
    html = html.trim(); // Never return a text node of whitespace as the result
    template.innerHTML = html;
    return template.content.firstChild;
};

function del_timing(obj){
    var xmlhttp = new XMLHttpRequest();
    var theUrl = "/api/timing/del";
    xmlhttp.open("POST", theUrl);
    var data = new FormData();
    data.append("timing", obj.id);
    xmlhttp.send(data);
    obj.parentNode.parentNode.parentNode.removeChild(obj.parentNode.parentNode);
}

function add_timing(){
    document.getElementById("addtiming").style.display="";
}

function close_timing(){
    document.getElementById("addtiming").style.display="none";
}

function save_timing(){
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            location.reload();
        };
    };
    var theUrl = "/api/timing/add";
    xmlhttp.open("POST", theUrl);
    var datas = {};
    datas["name"] = document.getElementById("name").value;
    datas["hour"] = document.getElementById("hour").value;
    datas["minute"] = document.getElementById("minute").value;
    datas["monday"] = document.getElementById("monday").value;
    datas["tuesday"] = document.getElementById("tuesday").value;
    datas["wednesday"] = document.getElementById("wednesday").value;
    datas["thursday"] = document.getElementById("thursday").value;
    datas["friday"] = document.getElementById("friday").value;
    datas["saturday"] = document.getElementById("saturday").value;
    datas["sunday"] = document.getElementById("sunday").value;
    var steps = []
    Array.from(document.getElementById("table_timing").querySelectorAll("tr.step")).forEach(function(obj){
        steps.push(obj.querySelectorAll("input")[0].value)
    });
    datas["steps"] = steps;
    var data = new FormData();
    data.append("timing", JSON.stringify(datas, null, 2))
    xmlhttp.send(data);
    document.getElementById("addtiming").style.display="none";
}

var steptiming = `
<tr class="step">
    <td></td>
    <td><input class="siimple-input siimple-input--fluid" value=""></td>
    <td class="minimal"><div class="siimple-btn--big icon-timing-del siimple--float-right" onclick="del_timing_step(this)"></div></td>
</tr>
`;

function add_timing_step(){
    document.getElementById("table_timing").appendChild(htmlToElement(steptiming));
}

function del_timing_step(obj){
    obj.parentNode.parentNode.parentNode.removeChild(obj.parentNode.parentNode)
}
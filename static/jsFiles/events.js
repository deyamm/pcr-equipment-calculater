// 网页中的生成策略按钮，根据网页中的材料数量获取刷图建议并显示到网页中
$("#getScheme").click(function () {
    getNeedCraft();
});

$("#otherInfoSet").click(function () {
    $("#otherInfoContainer").css("display", "block");
});

$("#otherInfoSetButton").click(function () {
    $("#otherInfoContainer").css("display", "none");
});
// 角色列表的关闭按钮
$("#listCloseButton").click(function () {
    $("#unitListContainer").css("display", "none");
    $("#pageCover").css("display", "none");
});
// 表单的关闭按钮
$("#infoCancelButton").click(function () {
    $("#infoFormContainer").css("display", "none");
});
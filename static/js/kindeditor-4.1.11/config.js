KindEditor.ready(function (K) {
    K.create('textarea[name="body"]', { /*css元素*/
        width: '1000px',
        height: '600px',
        uploadJson: '/admin/upload/kindeditor', /*请求url*/
    });
});
async function init(){
    console.log("Hello")
    link="process"
    obj2upload={"a":15}
    post_data(link,obj2upload,function(obj1){
        console.log(obj1)
    })
}
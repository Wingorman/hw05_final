function setClassList(classUl, classLi) {
  const ulTag = document.querySelectorAll('ul#posts_list')[0];
  const liTags = ulTag.querySelectorAll('li');
  classUl.split(" ").forEach(cls => {
    ulTag.classList.add(cls)
  })
  classLi.split(" ").forEach(cls => {
    console.log(cls)
    liTags.forEach(tag => {
      tag.classList.add(cls)
    })
  })
}

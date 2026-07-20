// Global vars
let selectedId = "none"
const domainWithPort = window.location.origin;
console.log(`Host: ${domainWithPort}`)
let lastGeneratedBlog = "none"

// Blog fetch function
function getTheBlog(blogId) {
  selectedId = blogId
  url = `${domainWithPort}/get-blog`
  jsonPayload = {
    "id": selectedId
  }
  // AJAX POST
  try {
    $.ajax({
      url: url,
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify(
        jsonPayload
      ),
      dataType: 'json'
    })
    .done(function(response) {
      //console.log('Data saved:', response);
      let htmlBlog = response.html;
      if(htmlBlog != "none"){ // file already exists
        // get and update all meta values in form
        $('#blogTitleInp').val(response.blog_title);
        $('#blogDescInp').val(response.head_desc);
        $('#ogImgInp').val(response.og_img);
        $('#keywordsInp').val(response.keywords);
        let can_href = response.canonical_href
        if(can_href.includes("http")){
          let parsedUrl = new URL(can_href);
          let rootDomain = parsedUrl.origin; 
          let pathComponent = parsedUrl.pathname.replace(/^\//, '');
          console.log("Root domain: ", rootDomain);
          $('#blogPathInp').val(pathComponent);
        }
        // Update summernote code dynamically
        $('#summernote').summernote('code', '');
        $('#summernote').summernote('code', htmlBlog);
      }
      else{
        alert(`No blog found for: ${selectedId}, you can create a NEW one.`);
      }
    })
    .fail(function(xhr, status, error) {
      console.error('Submission failed:', error);
    });
  }
  catch (error) {
    console.log("Caught error in caller:", error);
  }
}

// Save the blog 
function saveBlog() {

  url = `${domainWithPort}/update-blog`;
  var blogHTML = $('#summernote').summernote('code');
  let blogTitleInp = $('#blogTitleInp').val().trim();
  let blogDescInp = $('#blogDescInp').val().trim();
  let blogPathInp = $('#blogPathInp').val().trim();
  let ogImgInp = $('#ogImgInp').val().trim();
  let keywordsInp = $('#keywordsInp').val().trim();
  const isChecked = document.querySelector('#pageFindInp').checked;
  let pagefindVal = ""

  if(isChecked){
    pagefindVal = "data-pagefind-body"
  }

  lastGeneratedBlog = blogHTML
  jsonPayload = {
    "id": selectedId,
    "content": blogHTML,
    "title": blogTitleInp,
    "desc": blogDescInp,
    "path": blogPathInp,
    "ogimg": ogImgInp,
    "keywords": keywordsInp,
    "pagefind": pagefindVal
  }

  $.ajax({
    url: url,
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify(
      jsonPayload
    ),
    dataType: 'json'
  })
  .done(function(response) {
    if(response.stat == "ok"){
      alert("Blog Saved");
    }
    //alert(`Status: ${response.stat}`)
  })
  .fail(function(xhr, status, error) {
    console.error('Submission failed:', error);
  });
}

// Start operations when doc is ready
$(document).ready(function() {

  // Summernote initialization
  $('#summernote').summernote({
    height: 400,
    placeholder: 'Write your static blog draft here...',
    // 1. Ensure the resizing interaction system is explicitly enabled
    disableResizeImage: true, 
    // 2. Define the popup context menu toolbar that reveals the sizing anchors
    popover: {
      image: [
        ['image', ['resizeFull', 'resizeHalf', 'resizeQuarter', 'resizeNone']],
        ['float', ['floatLeft', 'floatRight', 'floatNone']],
        ['remove', ['removeMedia']]
      ]
    }
  });

  // Select the Blog element
  const selectElement = document.getElementById('blogSelect');
  selectElement.addEventListener('change', (event) => {
    const selectedValue = event.target.value;
    console.log(`Selected blog: ${selectedValue}`);
    if(selectedValue != "none"){
      // to implement the pop up if any blog is unsaved
      $('#blogTitleInp').val("");
      $('#blogDescInp').val("");
      $('#ogImgInp').val("");
      $('#keywordsInp').val("");
      $('#blogPathInp').val("");
      $('#summernote').summernote('code', '');
      getTheBlog(selectedValue);
    }
  });

  // Pop-up save changes
  $('#saveBlogBtn').on('click', function() {
    var blogHTML = $('#summernote').summernote('code');
    console.log(`Code from blog: ${blogHTML}`)
    if(selectedId == "none"){
      alert("No blog ID is selected. You may still write your blog and copy from the code section");
    }
    else if(blogHTML === '' || blogHTML == "<p><br></p>"){
      alert("Nothing to save!");
    }
    else if(blogHTML == lastGeneratedBlog){
      alert("There is no change after the last save");
    }
    else{
      //var modalElement = document.getElementById('saveChangesModal');
      console.log("Modal should be triggered");
      var myModal = new bootstrap.Modal("#saveChangesModal");
      myModal.show();
    }
  });

  // Save the blog
  $('#saveChConfirmBtn').on('click', function() {
    saveBlog();
  });

});


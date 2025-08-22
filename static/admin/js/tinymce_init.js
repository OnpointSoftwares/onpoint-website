(function(){
  if (typeof tinymce === 'undefined') { return; }
  // Initialize TinyMCE on any textarea.rich-text-editor in Django admin
  tinymce.init({
    selector: 'textarea.rich-text-editor',
    menubar: false,
    plugins: 'lists link table code preview fullscreen',
    toolbar: 'undo redo | bold italic underline | bullist numlist | link table | code preview fullscreen',
    branding: false,
    content_style: 'body { font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; font-size: 14px; }',
    height: 400,
    convert_urls: false
  });
})();

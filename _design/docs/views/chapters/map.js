function(doc) {
  var meta = doc.meta || {chapter:0, subsection: 0};
  emit([doc._id, meta.chapter, meta.subsection], doc.content.split('\n')[0].split('# ')[1]);

}

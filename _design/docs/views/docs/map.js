function(doc){
  if (doc.content){
    emit(doc._id, doc.content);
  }
}

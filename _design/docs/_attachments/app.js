function build_toc(toc_div){
  // Only make the TOC from the first 3 levels of headings
  var headers = $("h1,h2,h3");
  var node = $("<ul>");
  node.attr("class", "toc_2");
  node.attr("id", "sections");
  $('#' + toc_div).append(node);
  var level = 1;

  headers.each(function(e){
    var new_level = headers[e].tagName.match(/\d+/)[0];
    var anchor = $("<a>");
    // This isn't perfect - if you have two h2's with the same name
    // there'll be a clash
    var ref = headers[e].textContent.toLowerCase().replace(" ", "");

    anchor.attr("name", ref);
    $(headers[e]).prepend(anchor);

    if (level < new_level){
      var ul_node = $("<ul>");
      ul_node.attr("class", "toc_" + new_level);
      $(_.last($(".toc_" + level))).append(ul_node);
    }
    level = new_level;

    var new_node = $("<li>");
    var link_node = $("<a href='#" + ref + "'>" + headers[e].textContent + "</a>");

    if (level == 1) {
      var new_node = $("<div>");
      new_node.attr("id", "header");
      link_node.attr("id", "logo");
      new_node.append(link_node);
      $('#' + toc_div).prepend(new_node);
    } else {
      new_node.append(link_node);
      $(_.last($(".toc_" + level))).append(new_node);
    }
  });

}

var Doc = Backbone.Model.extend({
 initialize: function(doc) {
   this.set({md: doc});
 }
});

var DocCollection = Backbone.Collection.extend({
  model: Doc,
  url: "docs",
  key: null,
  doreduce: false,
  initialize: function(models, options){
    Backbone.Collection.prototype.initialize.apply(this, [models, options]);
    this.key = options.key;
  },
  error : function(jqXHR, textStatus, errorThrown){
    Backbone.couch.log(["jqXHR", jqXHR]);
    Backbone.couch.log(["textStatus", textStatus]);
    Backbone.couch.log(["errorThrown", errorThrown]);
    return null
  }
});

var Documentation = Backbone.View.extend({
  initialize: function(settings) {
    _.bindAll(this);
    _.extend(this, Backbone.Events);

    this.converter = new Markdown.Converter();

    this.collection.bind('change', this.render);
    this.collection.bind('add', this.render);
    this.collection.bind('remove', this.render);
    this.collection.bind('reset', this.render);
    this.collection.fetch();
  },
  render: function() {
    var doc = this.collection.at(0);
    $(this.el).html(this.converter.makeHtml(doc.get('md')));
    build_toc("nav");
  }
});

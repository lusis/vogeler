function(doc) {
	if (doc.doc_type == "SystemRecord") {
		emit(doc._id, doc);
	}
}

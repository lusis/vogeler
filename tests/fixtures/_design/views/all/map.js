function(doc) {
	if (doc.doc_type == "test_document_type") {
		emit(doc._id, doc);
	}
}

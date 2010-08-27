function(doc) {
	if (doc.doc_type == 'SystemRecord') {
		if (doc.system_name) {
			emit(doc.system_name, null)
		}
	}
}

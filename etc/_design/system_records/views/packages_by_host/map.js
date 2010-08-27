function(doc) {
	if (doc.doc_type == 'SystemRecord') {
		if (doc.system_name && doc.system_packages) {
			emit(doc.system_name, doc.system_packages)
		}
	}
}

package com.docsearch.app.service;

import com.docsearch.app.model.Document;

import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

class TenantIndex {
    final ConcurrentHashMap<String, Document> docs = new ConcurrentHashMap<>();
    final ConcurrentHashMap<String, Set<String>> wordIndex = new ConcurrentHashMap<>();
    final ConcurrentHashMap<String, Set<String>> trigramIndex = new ConcurrentHashMap<>();
}

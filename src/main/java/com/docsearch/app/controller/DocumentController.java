package com.docsearch.app.controller;

import com.docsearch.app.dto.CreateDocumentRequest;
import com.docsearch.app.dto.SearchResult;
import com.docsearch.app.model.Document;
import com.docsearch.app.service.DocumentService;
import com.docsearch.app.service.TenantService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
public class DocumentController {

    private final DocumentService documentService;
    private final TenantService tenantService;

    @PostMapping("/documents")
    public ResponseEntity<Document> indexDocument(
            @RequestHeader("X-Tenant-Id") String tenantId,
            @RequestBody CreateDocumentRequest request) {
        if (!tenantService.exists(tenantId)) return ResponseEntity.notFound().build();
        return documentService.index(tenantId, request.getTitle(), request.getContent())
                .map(doc -> ResponseEntity.status(HttpStatus.CREATED).body(doc))
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/documents/{id}")
    public ResponseEntity<Document> getDocument(
            @RequestHeader("X-Tenant-Id") String tenantId,
            @PathVariable String id) {
        if (!tenantService.exists(tenantId)) return ResponseEntity.notFound().build();
        return documentService.findById(tenantId, id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/documents/{id}")
    public ResponseEntity<Void> deleteDocument(
            @RequestHeader("X-Tenant-Id") String tenantId,
            @PathVariable String id) {
        if (!tenantService.exists(tenantId)) return ResponseEntity.notFound().build();
        return documentService.delete(tenantId, id)
                ? ResponseEntity.noContent().build()
                : ResponseEntity.notFound().build();
    }

    @GetMapping("/search")
    public ResponseEntity<List<SearchResult>> search(
            @RequestParam String q,
            @RequestParam String tenant) {
        return documentService.search(tenant, q)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}

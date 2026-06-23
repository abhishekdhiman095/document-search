package com.docsearch.app.model;

import lombok.Builder;
import lombok.Data;

import java.time.Instant;

@Data
@Builder
public class Document {
    private String id;
    private String tenantId;
    private String title;
    private String content;
    private Instant createdAt;
}

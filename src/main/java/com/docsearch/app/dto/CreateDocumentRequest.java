package com.docsearch.app.dto;

import lombok.Data;

@Data
public class CreateDocumentRequest {
    private String title;
    private String content;
}

package com.docsearch.app.dto;

import com.docsearch.app.model.Document;
import lombok.Data;

@Data
public class SearchResult {
    private final Document document;
    private final int score;
}

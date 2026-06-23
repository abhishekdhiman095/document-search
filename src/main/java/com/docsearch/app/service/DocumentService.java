package com.docsearch.app.service;

import com.docsearch.app.dto.SearchResult;
import com.docsearch.app.model.Document;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Service
@RequiredArgsConstructor
public class DocumentService {

    private final TenantService tenantService;

    @Value("${search.max-edit-distance:2}")
    private int maxEditDistance;

    public Optional<Document> index(String tenantId, String title, String content) {
        return tenantService.getIndex(tenantId).map(idx -> {
            Document doc = Document.builder()
                    .id(UUID.randomUUID().toString())
                    .tenantId(tenantId)
                    .title(title)
                    .content(content)
                    .createdAt(Instant.now())
                    .build();
            idx.docs.put(doc.getId(), doc);
            addToIndex(idx, doc.getId(), title + " " + content);
            return doc;
        });
    }

    public Optional<Document> findById(String tenantId, String id) {
        return tenantService.getIndex(tenantId)
                .map(idx -> idx.docs.get(id));
    }

    public boolean delete(String tenantId, String id) {
        return tenantService.getIndex(tenantId).map(idx -> {
            Document doc = idx.docs.remove(id);
            if (doc == null) return false;
            removeFromIndex(idx, id, doc.getTitle() + " " + doc.getContent());
            return true;
        }).orElse(false);
    }

    /**
     * Three-pass scoring per query token:
     *   1. Exact word match          → +10 pts
     *   2. Edit distance word match  → +(10 - distance * 3) pts  (trigram pre-filter)
     *   3. Raw trigram overlap       → +1 pt per shared trigram
     */
    public Optional<List<SearchResult>> search(String tenantId, String query) {
        return tenantService.getIndex(tenantId).map(idx -> {
            Map<String, Integer> scores = new HashMap<>();

            for (String token : tokenize(query)) {
                Set<String> tokenTrigrams = new HashSet<>(trigrams(token));

                // Pass 1 & 2 — word index
                for (Map.Entry<String, Set<String>> entry : idx.wordIndex.entrySet()) {
                    String indexedWord = entry.getKey();
                    int dist = levenshtein(token, indexedWord);

                    if (dist == 0) {
                        // Exact word match
                        for (String docId : entry.getValue()) scores.merge(docId, 10, Integer::sum);
                    } else if (dist <= maxEditDistance) {
                        // Fuzzy word match — score decreases with distance
                        int pts = Math.max(1, 10 - dist * 3);
                        for (String docId : entry.getValue()) scores.merge(docId, pts, Integer::sum);
                    }
                }

                // Pass 3 — raw trigram overlap (catches partial / substring matches)
                for (String trigram : tokenTrigrams) {
                    Set<String> hits = idx.trigramIndex.getOrDefault(trigram, Set.of());
                    for (String docId : hits) scores.merge(docId, 1, Integer::sum);
                }
            }

            return scores.entrySet().stream()
                    .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
                    .map(e -> {
                        Document doc = idx.docs.get(e.getKey());
                        return doc != null ? new SearchResult(doc, e.getValue()) : null;
                    })
                    .filter(Objects::nonNull)
                    .toList();
        });
    }

    // --- Index maintenance ---

    private void addToIndex(TenantIndex idx, String docId, String text) {
        for (String token : tokenize(text)) {
            idx.wordIndex.computeIfAbsent(token, k -> ConcurrentHashMap.newKeySet()).add(docId);
            for (String trigram : trigrams(token)) {
                idx.trigramIndex.computeIfAbsent(trigram, k -> ConcurrentHashMap.newKeySet()).add(docId);
            }
        }
    }

    private void removeFromIndex(TenantIndex idx, String docId, String text) {
        for (String token : tokenize(text)) {
            idx.wordIndex.computeIfPresent(token, (k, v) -> { v.remove(docId); return v.isEmpty() ? null : v; });
            for (String trigram : trigrams(token)) {
                idx.trigramIndex.computeIfPresent(trigram, (k, v) -> { v.remove(docId); return v.isEmpty() ? null : v; });
            }
        }
    }

    // --- Text processing ---

    private String[] tokenize(String text) {
        return text.toLowerCase().split("[^a-z0-9]+");
    }

    private List<String> trigrams(String word) {
        List<String> result = new ArrayList<>();
        for (int i = 0; i <= word.length() - 3; i++) {
            result.add(word.substring(i, i + 3));
        }
        return result;
    }

    // --- Levenshtein edit distance (iterative, O(m*n) time, O(n) space) ---

    private int levenshtein(String a, String b) {
        int m = a.length(), n = b.length();
        int[] prev = new int[n + 1];
        int[] curr = new int[n + 1];
        for (int j = 0; j <= n; j++) prev[j] = j;
        for (int i = 1; i <= m; i++) {
            curr[0] = i;
            for (int j = 1; j <= n; j++) {
                if (a.charAt(i - 1) == b.charAt(j - 1)) {
                    curr[j] = prev[j - 1];
                } else {
                    curr[j] = 1 + Math.min(prev[j - 1], Math.min(prev[j], curr[j - 1]));
                }
            }
            int[] tmp = prev; prev = curr; curr = tmp;
        }
        return prev[n];
    }
}

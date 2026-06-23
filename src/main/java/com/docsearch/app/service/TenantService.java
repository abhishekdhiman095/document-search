package com.docsearch.app.service;

import com.docsearch.app.model.Tenant;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class TenantService {

    private final ConcurrentHashMap<String, Tenant> tenants = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, TenantIndex> indexes = new ConcurrentHashMap<>();

    public Tenant register(String name) {
        Tenant tenant = Tenant.builder()
                .id(UUID.randomUUID().toString())
                .name(name)
                .createdAt(Instant.now())
                .build();
        tenants.put(tenant.getId(), tenant);
        indexes.put(tenant.getId(), new TenantIndex());
        return tenant;
    }

    public Optional<Tenant> findById(String id) {
        return Optional.ofNullable(tenants.get(id));
    }

    public List<Tenant> findAll() {
        return List.copyOf(tenants.values());
    }

    public boolean delete(String id) {
        if (tenants.remove(id) == null) return false;
        indexes.remove(id);
        return true;
    }

    public boolean exists(String id) {
        return tenants.containsKey(id);
    }

    /** Returns the index for an existing tenant, empty if tenant not found. */
    public Optional<TenantIndex> getIndex(String tenantId) {
        return Optional.ofNullable(indexes.get(tenantId));
    }
}

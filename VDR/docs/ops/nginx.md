# Nginx Ops Notes

These snippets show how to enable modern transport and compression when serving
chart tiles.

## Compression with Brotli and Zstandard

```nginx
load_module modules/ngx_http_brotli_filter_module.so;
load_module modules/ngx_http_brotli_static_module.so;
load_module modules/ngx_http_zstd_filter_module.so;
load_module modules/ngx_http_zstd_static_module.so;

server {
    brotli on;
    brotli_static on;
    brotli_types application/json application/x-protobuf;

    zstd  on;
    zstd_static on;
    zstd_types application/json application/x-protobuf;
}
```

## HTTP/3

```nginx
server {
    listen 443 ssl http2;         # HTTP/2 fallback
    listen 443 quic reuseport;    # HTTP/3
    ssl_certificate     /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;

    add_header Alt-Svc 'h3=":443"';
}
```

Enable [Brotli](https://github.com/google/ngx_brotli) and
[Zstandard](https://github.com/tokers/zstd-nginx-module) modules at build time
or via dynamic modules.

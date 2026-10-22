package com.myrag.backend.common;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.util.Date;

@Component
public class JwtUtil {
    // 签名密钥，实际项目应放在配置文件里
    private static final String SECRET = "my_rag_project_secret_key_must_be_long_enough_123456";
    private static final SecretKey KEY = Keys.hmacShaKeyFor(SECRET.getBytes());
    
    // Token 有效期：24小时
    private static final long EXPIRATION_TIME = 86400000;

    // 生成 Token
    public String generateToken(Long userId, String username) {
        return Jwts.builder()
                .subject(username)
                .claim("userId", userId)
                .issuedAt(new Date())
                .expiration(new Date(System.currentTimeMillis() + EXPIRATION_TIME))
                .signWith(KEY)
                .compact();
    }

    // 解析 Token，获取用户ID
    public Long getUserIdFromToken(String token) {
        Claims claims = Jwts.parser()
                .verifyWith(KEY)
                .build()
                .parseSignedClaims(token)
                .getPayload();
        return claims.get("userId", Long.class);
    }
}
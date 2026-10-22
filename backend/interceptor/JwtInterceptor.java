package com.myrag.backend.interceptor;

import com.myrag.backend.common.JwtUtil;
import com.myrag.backend.common.UserContext;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

@Component
public class JwtInterceptor implements HandlerInterceptor {

    @Autowired
    private JwtUtil jwtUtil;

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        // 1. 获取请求头中的 Token (格式一般为 "Bearer eyJ...")
        String authHeader = request.getHeader("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            response.setStatus(401);
            response.getWriter().write("{\"code\":401,\"message\":\"未登录或Token缺失\"}");
            return false; // 拦截请求
        }

        // 2. 提取真正的 Token 字符串
        String token = authHeader.substring(7);
        try {
            // 3. 解析 Token 获取 userId
            Long userId = jwtUtil.getUserIdFromToken(token);
            // 4. 存入 ThreadLocal，供 Controller 使用
            UserContext.setUserId(userId);
            return true; // 放行
        } catch (Exception e) {
            response.setStatus(401);
            response.getWriter().write("{\"code\":401,\"message\":\"Token无效或已过期\"}");
            return false; // 拦截请求
        }
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) {
        // 请求结束，清理 ThreadLocal 防止内存泄漏
        UserContext.clear();
    }
}
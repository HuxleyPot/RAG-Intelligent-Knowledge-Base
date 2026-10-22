package com.myrag.backend.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.myrag.backend.common.Result;
import com.myrag.backend.common.UserContext;
import com.myrag.backend.entity.KnowledgeBase;
import com.myrag.backend.entity.KnowledgeBaseDTO;
import com.myrag.backend.mapper.KnowledgeBaseMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/knowledge-bases")
public class KnowledgeBaseController {

    @Autowired
    private KnowledgeBaseMapper kbMapper;

    // 1. 获取当前用户的知识库列表
    @GetMapping
    public Result<List<KnowledgeBase>> listAll() {
        Long currentUserId = UserContext.getUserId();
        if (currentUserId == null) {
            return Result.error("未获取到用户信息，请重新登录");
        }

        List<KnowledgeBase> list = kbMapper.selectList(
                new LambdaQueryWrapper<KnowledgeBase>()
                        .eq(KnowledgeBase::getOwnerId, currentUserId)
        );
        return Result.success(list);
    }

    // 2. 创建知识库
    @PostMapping
    public Result<String> create(@RequestBody KnowledgeBaseDTO dto) {
        Long currentUserId = UserContext.getUserId();
        if (currentUserId == null) {
            return Result.error("未获取到用户信息，请重新登录");
        }

        KnowledgeBase kb = new KnowledgeBase();
        kb.setName(dto.getName());
        kb.setDescription(dto.getDescription());
        kb.setOwnerId(currentUserId); // 使用真实的登录用户ID
        kb.setCreatedAt(LocalDateTime.now());

        kbMapper.insert(kb);
        return Result.success("创建知识库成功");
    }
}

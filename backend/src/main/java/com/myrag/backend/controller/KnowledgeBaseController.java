package com.myrag.backend.controller;

import com.myrag.backend.common.Result;
import com.myrag.backend.entity.KnowledgeBase;
import com.myrag.backend.entity.KnowledgeBaseDTO;
import com.myrag.backend.mapper.KnowledgeBaseMapper;
import com.myrag.backend.common.UserContext;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/knowledge-bases")
public class KnowledgeBaseController {

    @Autowired
    private KnowledgeBaseMapper kbMapper;

    // 1. 获取知识库列表
    @GetMapping
    public Result<List<KnowledgeBase>> listAll() {
        // 暂时写死查询 ownerId=1 (admin) 的数据
        List<KnowledgeBase> list = kbMapper.selectList(null);
        return Result.success(list);
    }

    // 2. 创建知识库
    @PostMapping
    public Result<String> create(@RequestBody KnowledgeBaseDTO dto) {
        KnowledgeBase kb = new KnowledgeBase();
        kb.setName(dto.getName());
        kb.setDescription(dto.getDescription());
        kb.setOwnerId(1L); // 暂时写死为admin
        kb.setCreatedAt(LocalDateTime.now());
        
        kbMapper.insert(kb);
        return Result.success("创建知识库成功");
    }
}
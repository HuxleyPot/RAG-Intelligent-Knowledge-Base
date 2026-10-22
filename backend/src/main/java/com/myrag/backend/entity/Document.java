package com.myrag.backend.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("kb_document")
public class Document {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long kbId;
    private String filename;
    private String filePath;
    private String status;      // 状态: PROCESSING, AVAILABLE, FAILED
    private String errorMessage;
    private LocalDateTime createdAt;
}
"""
Template Management Endpoints
Upload, search, manage thumbnail templates
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.template import Template
from app.services.template_service import template_service, TemplateServiceError
from datetime import datetime, timezone

router = APIRouter()


@router.post("/upload", response_model=Dict[str, Any])
async def upload_template(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form("uncategorized"),
    tags: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Upload a new template to the secret bank
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
        
        # Upload template
        result = await template_service.upload_template(
            file_content=file_content,
            filename=file.filename or "unknown.jpg",
            user_id=current_user.id,
            title=title,
            description=description,
            category=category,
            tags=tag_list,
            auto_analyze=True
        )
        
        # Save to database
        new_template = Template(
            id=result["template"]["id"],
            user_id=current_user.id,
            title=title,
            description=description or "",
            category=category or "uncategorized",
            tags=tag_list,
            file_path=result["template"]["file_path"],
            file_size=result["template"]["file_size"],
            status="uploaded",
            analysis_status=result["template"]["analysis_status"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db.add(new_template)
        await db.commit()
        await db.refresh(new_template)
        
        return {
            "success": True,
            "data": result,
            "message": "Template uploaded successfully"
        }
        
    except TemplateServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/batch-upload", response_model=Dict[str, Any])
async def batch_upload_templates(
    files: List[UploadFile] = File(...),
    category: Optional[str] = Form("uncategorized"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Upload multiple templates at once (drag & drop)
    """
    try:
        results = []
        
        for file in files:
            try:
                file_content = await file.read()
                
                # Auto-generate title from filename
                title = file.filename.rsplit('.', 1)[0] if file.filename else "Untitled"
                
                result = await template_service.upload_template(
                    file_content=file_content,
                    filename=file.filename or "unknown.jpg",
                    user_id=current_user.id,
                    title=title,
                    category=category,
                    auto_analyze=True
                )
                
                # Save to database
                new_template = Template(
                    id=result["template"]["id"],
                    user_id=current_user.id,
                    title=title,
                    category=category or "uncategorized",
                    file_path=result["template"]["file_path"],
                    file_size=result["template"]["file_size"],
                    status="uploaded",
                    analysis_status=result["template"]["analysis_status"],
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                
                db.add(new_template)
                
                results.append({
                    "filename": file.filename,
                    "status": "success",
                    "template_id": result["template"]["id"]
                })
                
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": str(e)
                })
        
        await db.commit()
        
        successful = len([r for r in results if r["status"] == "success"])
        
        return {
            "success": True,
            "data": {
                "results": results,
                "total": len(files),
                "successful": successful,
                "failed": len(files) - successful
            },
            "message": f"Uploaded {successful}/{len(files)} templates successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch upload failed: {str(e)}")


@router.get("/search", response_model=Dict[str, Any])
async def search_templates(
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Search templates with filters
    """
    try:
        # Build query
        stmt = select(Template).where(Template.status != "deleted")
        
        # Apply filters
        if query:
            stmt = stmt.where(
                or_(
                    Template.title.ilike(f"%{query}%"),
                    Template.description.ilike(f"%{query}%")
                )
            )
        
        if category:
            stmt = stmt.where(Template.category == category)
        
        # Execute query
        result = await db.execute(stmt.offset(offset).limit(limit))
        templates = result.scalars().all()
        
        # Get total count
        count_stmt = select(func.count(Template.id)).where(Template.status != "deleted")
        if query:
            count_stmt = count_stmt.where(
                or_(
                    Template.title.ilike(f"%{query}%"),
                    Template.description.ilike(f"%{query}%")
                )
            )
        if category:
            count_stmt = count_stmt.where(Template.category == category)
        
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0
        
        # Format results
        formatted_templates = []
        for template in templates:
            formatted_templates.append({
                "id": template.id,
                "title": template.title,
                "description": template.description,
                "category": template.category,
                "tags": template.tags or [],
                "thumbnail_url": f"/api/v1/templates/{template.id}/thumbnail",
                "file_path": template.file_path,
                "created_at": template.created_at.isoformat(),
                "view_count": template.view_count or 0,
                "download_count": template.download_count or 0,
                "analysis_status": template.analysis_status
            })
        
        return {
            "success": True,
            "results": formatted_templates,
            "metadata": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + len(templates) < total
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/{template_id}", response_model=Dict[str, Any])
async def get_template(
    template_id: str,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get template details by ID
    """
    try:
        result = await db.execute(
            select(Template).where(Template.id == template_id)
        )
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Increment view count
        if current_user:
            template.view_count = (template.view_count or 0) + 1
            await db.commit()
        
        return {
            "success": True,
            "data": {
                "id": template.id,
                "title": template.title,
                "description": template.description,
                "category": template.category,
                "tags": template.tags or [],
                "file_path": template.file_path,
                "thumbnail_url": f"/api/v1/templates/{template.id}/thumbnail",
                "created_at": template.created_at.isoformat(),
                "view_count": template.view_count or 0,
                "download_count": template.download_count or 0,
                "analysis_status": template.analysis_status
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get template: {str(e)}")


@router.get("/{template_id}/thumbnail")
async def get_template_thumbnail(
    template_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get template thumbnail image
    """
    try:
        result = await db.execute(
            select(Template).where(Template.id == template_id)
        )
        template = result.scalar_one_or_none()
        
        if not template or not template.file_path:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return FileResponse(
            template.file_path,
            media_type="image/jpeg",
            filename=f"{template.title}.jpg"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get thumbnail: {str(e)}")


@router.put("/{template_id}", response_model=Dict[str, Any])
async def update_template(
    template_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update template metadata
    """
    try:
        result = await db.execute(
            select(Template).where(Template.id == template_id)
        )
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Update fields
        if title:
            template.title = title
        if description:
            template.description = description
        if category:
            template.category = category
        if tags:
            template.tags = [tag.strip() for tag in tags.split(",")]
        
        template.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(template)
        
        return {
            "success": True,
            "data": {
                "id": template.id,
                "title": template.title,
                "description": template.description,
                "category": template.category,
                "tags": template.tags
            },
            "message": "Template updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")


@router.delete("/{template_id}", response_model=Dict[str, Any])
async def delete_template(
    template_id: str,
    hard_delete: bool = Query(False, description="Permanently delete (true) or soft delete (false)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Delete template (soft delete by default)
    """
    try:
        result = await db.execute(
            select(Template).where(Template.id == template_id)
        )
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        if hard_delete:
            # Hard delete
            await db.delete(template)
        else:
            # Soft delete
            template.status = "deleted"
            template.deleted_at = datetime.now(timezone.utc)
        
        await db.commit()
        
        return {
            "success": True,
            "message": f"Template {'permanently deleted' if hard_delete else 'moved to trash'}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.get("/categories/list", response_model=Dict[str, Any])
async def get_categories(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get all template categories with counts
    """
    try:
        result = await db.execute(
            select(
                Template.category,
                func.count(Template.id).label('count')
            )
            .where(Template.status != "deleted")
            .group_by(Template.category)
        )
        
        categories = []
        for row in result:
            categories.append({
                "name": row.category,
                "count": row.count
            })
        
        return {
            "success": True,
            "data": categories
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")


@router.get("/stats/overview", response_model=Dict[str, Any])
async def get_template_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get template bank statistics
    """
    try:
        # Total templates
        total_result = await db.execute(
            select(func.count(Template.id)).where(Template.status != "deleted")
        )
        total = total_result.scalar() or 0
        
        # Total views
        views_result = await db.execute(
            select(func.sum(Template.view_count)).where(Template.status != "deleted")
        )
        total_views = views_result.scalar() or 0
        
        # Total downloads
        downloads_result = await db.execute(
            select(func.sum(Template.download_count)).where(Template.status != "deleted")
        )
        total_downloads = downloads_result.scalar() or 0
        
        # Categories count
        categories_result = await db.execute(
            select(func.count(func.distinct(Template.category)))
            .where(Template.status != "deleted")
        )
        categories_count = categories_result.scalar() or 0
        
        return {
            "success": True,
            "data": {
                "total_templates": total,
                "total_views": total_views,
                "total_downloads": total_downloads,
                "categories_count": categories_count
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('board', function (Blueprint $table) {
            $table->id();
            $table->foreignId('area_id')->unique()->constrained('area')->cascadeOnDelete();
            $table->string('name', 100);
            $table->text('description')->nullable();
            $table->string('default_swimlane', 30)->default('NINGUNO');
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });

        Schema::create('board_column', function (Blueprint $table) {
            $table->id();
            $table->foreignId('board_id')->constrained('board')->cascadeOnDelete();
            $table->foreignId('maps_to_status_id')->constrained('ticket_status')->cascadeOnDelete();
            $table->string('custom_name', 100)->nullable();
            $table->text('description')->nullable();
            $table->integer('position');
            $table->integer('wip_limit')->nullable();
            $table->string('wip_scope', 30)->default('COLUMNA');
            $table->boolean('is_system_managed')->default(false);
            $table->json('visible_to_role_codes')->nullable();
            $table->string('color_hex', 10)->nullable();
            $table->json('entry_rules')->nullable();
            $table->json('exit_rules')->nullable();
            $table->boolean('is_active')->default(true);
            $table->timestamps();

            $table->unique(['board_id', 'position']);
        });

        Schema::create('board_card_position', function (Blueprint $table) {
            $table->id();
            $table->foreignId('ticket_id')->unique()->constrained('ticket')->cascadeOnDelete();
            $table->foreignId('board_column_id')->constrained('board_column')->cascadeOnDelete();
            $table->decimal('position', 12, 6);
            $table->foreignId('moved_by')->constrained('user')->cascadeOnDelete();
            $table->timestamp('moved_at')->useCurrent();
        });

        Schema::create('board_view_preference', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained('user')->cascadeOnDelete();
            $table->foreignId('board_id')->constrained('board')->cascadeOnDelete();
            $table->json('filters')->nullable();
            $table->string('swimlane_mode', 30)->nullable();
            $table->timestamps();

            $table->unique(['user_id', 'board_id']);
        });

        Schema::create('checklist_template', function (Blueprint $table) {
            $table->id();
            $table->foreignId('ticket_type_id')->constrained('ticket_type')->cascadeOnDelete();
            $table->string('name', 150);
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });

        Schema::create('checklist_template_item', function (Blueprint $table) {
            $table->id();
            $table->foreignId('template_id')->constrained('checklist_template')->cascadeOnDelete();
            $table->text('text');
            $table->boolean('is_required')->default(false);
            $table->boolean('requires_evidence')->default(false);
            $table->integer('position')->default(0);
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });

        Schema::create('checklist_item', function (Blueprint $table) {
            $table->id();
            $table->foreignId('ticket_id')->constrained('ticket')->cascadeOnDelete();
            $table->foreignId('template_item_id')->nullable()->constrained('checklist_template_item')->nullOnDelete();
            $table->text('text');
            $table->boolean('is_required')->default(false);
            $table->boolean('requires_evidence')->default(false);
            $table->boolean('is_completed')->default(false);
            $table->foreignId('completed_by')->nullable()->constrained('user')->nullOnDelete();
            $table->dateTime('completed_at')->nullable();
            $table->integer('position')->default(0);
            $table->timestamps();
        });

        Schema::create('ticket_attachment', function (Blueprint $table) {
            $table->id();
            $table->foreignId('ticket_id')->constrained('ticket')->cascadeOnDelete();
            $table->foreignId('checklist_item_id')->nullable()->constrained('checklist_item')->nullOnDelete();
            $table->string('storage_path', 500);
            $table->string('original_filename', 255);
            $table->string('mime_type', 100);
            $table->unsignedBigInteger('file_size_bytes');
            $table->char('checksum_sha256', 64);
            $table->string('attachment_kind', 50)->default('OTRO');
            $table->foreignId('uploaded_by')->constrained('user')->cascadeOnDelete();
            $table->timestamp('uploaded_at')->useCurrent();
            $table->softDeletes();
        });

        Schema::create('ticket_comment', function (Blueprint $table) {
            $table->id();
            $table->foreignId('ticket_id')->constrained('ticket')->cascadeOnDelete();
            $table->foreignId('user_id')->constrained('user')->cascadeOnDelete();
            $table->text('body');
            $table->boolean('is_internal')->default(false);
            $table->json('mentioned_user_ids')->nullable();
            $table->timestamp('created_at')->useCurrent();
            $table->softDeletes();
        });

        Schema::create('work_log', function (Blueprint $table) {
            $table->id();
            $table->foreignId('ticket_id')->constrained('ticket')->cascadeOnDelete();
            $table->foreignId('user_id')->constrained('user')->cascadeOnDelete();
            $table->date('work_date');
            $table->decimal('hours', 6, 2);
            $table->text('description')->nullable();
            $table->decimal('cost', 12, 2)->nullable();
            $table->timestamp('created_at')->useCurrent();
        });

        Schema::create('quotation', function (Blueprint $table) {
            $table->id();
            $table->foreignId('ticket_id')->constrained('ticket')->cascadeOnDelete();
            $table->foreignId('vendor_id')->constrained('vendor')->cascadeOnDelete();
            $table->decimal('amount', 14, 2);
            $table->string('currency', 10)->default('BOB');
            $table->integer('delivery_days')->nullable();
            $table->string('payment_terms', 150)->nullable();
            $table->string('warranty', 150)->nullable();
            $table->foreignId('attachment_id')->nullable()->constrained('ticket_attachment')->nullOnDelete();
            $table->boolean('is_awarded')->default(false);
            $table->text('award_justification')->nullable();
            $table->foreignId('created_by')->constrained('user')->cascadeOnDelete();
            $table->timestamp('created_at')->useCurrent();
        });

        Schema::create('purchase_order', function (Blueprint $table) {
            $table->id();
            $table->foreignId('ticket_id')->unique()->constrained('ticket')->cascadeOnDelete();
            $table->string('po_number', 50)->unique();
            $table->foreignId('vendor_id')->constrained('vendor')->cascadeOnDelete();
            $table->foreignId('quotation_id')->nullable()->constrained('quotation')->nullOnDelete();
            $table->decimal('total_amount', 14, 2);
            $table->string('currency', 10)->default('BOB');
            $table->foreignId('issued_by')->constrained('user')->cascadeOnDelete();
            $table->dateTime('issued_at');
            $table->date('committed_delivery_date')->nullable();
            $table->foreignId('pdf_attachment_id')->nullable()->constrained('ticket_attachment')->nullOnDelete();
            $table->string('status', 30)->default('EMITIDA');
            $table->timestamps();
        });

        Schema::create('goods_receipt', function (Blueprint $table) {
            $table->id();
            $table->foreignId('ticket_id')->constrained('ticket')->cascadeOnDelete();
            $table->foreignId('purchase_order_id')->constrained('purchase_order')->cascadeOnDelete();
            $table->dateTime('received_at');
            $table->foreignId('received_by')->constrained('user')->cascadeOnDelete();
            $table->boolean('is_partial')->default(false);
            $table->string('invoice_number', 50)->nullable();
            $table->decimal('invoice_amount', 14, 2)->nullable();
            $table->text('notes')->nullable();
            $table->foreignId('attachment_id')->nullable()->constrained('ticket_attachment')->nullOnDelete();
            $table->timestamps();
        });

        Schema::create('vendor_evaluation', function (Blueprint $table) {
            $table->id();
            $table->foreignId('ticket_id')->constrained('ticket')->cascadeOnDelete();
            $table->foreignId('vendor_id')->constrained('vendor')->cascadeOnDelete();
            $table->unsignedTinyInteger('score_delivery');
            $table->unsignedTinyInteger('score_quality');
            $table->unsignedTinyInteger('score_price');
            $table->text('comment')->nullable();
            $table->foreignId('evaluated_by')->constrained('user')->cascadeOnDelete();
            $table->dateTime('evaluated_at');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('vendor_evaluation');
        Schema::dropIfExists('goods_receipt');
        Schema::dropIfExists('purchase_order');
        Schema::dropIfExists('quotation');
        Schema::dropIfExists('work_log');
        Schema::dropIfExists('ticket_comment');
        Schema::dropIfExists('ticket_attachment');
        Schema::dropIfExists('checklist_item');
        Schema::dropIfExists('checklist_template_item');
        Schema::dropIfExists('checklist_template');
        Schema::dropIfExists('board_view_preference');
        Schema::dropIfExists('board_card_position');
        Schema::dropIfExists('board_column');
        Schema::dropIfExists('board');
    }
};
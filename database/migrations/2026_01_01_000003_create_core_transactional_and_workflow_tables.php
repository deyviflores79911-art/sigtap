<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('ticket_status', function (Blueprint $table) {
            $table->id();
            $table->string('code', 50)->unique();
            $table->string('name', 100);
            $table->text('description')->nullable();
            $table->boolean('is_initial')->default(false);
            $table->boolean('is_terminal')->default(false);
            $table->boolean('stops_sla_clock')->default(false);
            $table->string('color_hex', 10)->nullable();
            $table->integer('position')->default(0);
            $table->timestamps();
        });

        Schema::create('workflow_transition', function (Blueprint $table) {
            $table->id();
            $table->foreignId('area_id')->nullable()->constrained('area')->nullOnDelete();
            $table->foreignId('from_status_id')->constrained('ticket_status')->cascadeOnDelete();
            $table->foreignId('to_status_id')->constrained('ticket_status')->cascadeOnDelete();
            $table->json('allowed_role_codes')->nullable();
            $table->json('guard_expression')->nullable();
            $table->boolean('requires_comment')->default(false);
            $table->json('effect_handlers')->nullable();
            $table->boolean('is_active')->default(true);
            $table->dateTime('valid_from')->nullable();
            $table->dateTime('valid_to')->nullable();
            $table->timestamps();
        });

        Schema::create('ticket', function (Blueprint $table) {
            $table->id();
            $table->uuid('uuid')->unique();
            $table->string('code', 50)->unique();
            $table->foreignId('area_id')->constrained('area')->cascadeOnDelete();
            $table->foreignId('ticket_type_id')->constrained('ticket_type')->cascadeOnDelete();
            $table->foreignId('category_id')->nullable()->constrained('category')->nullOnDelete();
            $table->foreignId('priority_id')->nullable()->constrained('priority')->nullOnDelete();
            $table->foreignId('status_id')->constrained('ticket_status')->cascadeOnDelete();
            $table->string('title', 200);
            $table->text('description');
            $table->foreignId('requester_id')->constrained('user')->cascadeOnDelete();
            $table->foreignId('assignee_id')->nullable()->constrained('user')->nullOnDelete();
            $table->foreignId('asset_id')->nullable()->constrained('asset')->nullOnDelete();
            $table->foreignId('location_id')->nullable()->constrained('location')->nullOnDelete();
            $table->foreignId('cost_center_id')->nullable()->constrained('cost_center')->nullOnDelete();
            $table->foreignId('vendor_id')->nullable()->constrained('vendor')->nullOnDelete();
            $table->decimal('estimated_cost', 14, 2)->nullable();
            $table->decimal('actual_cost', 14, 2)->nullable();
            $table->string('currency', 10)->default('BOB');
            $table->json('custom_fields')->nullable();
            $table->foreignId('linked_ticket_id')->nullable()->constrained('ticket')->nullOnDelete();
            $table->string('link_type', 50)->nullable();
            $table->integer('approval_round')->default(0);
            $table->integer('rework_count')->default(0);
            $table->dateTime('due_date')->nullable();
            $table->dateTime('first_response_at')->nullable();
            $table->dateTime('execution_started_at')->nullable();
            $table->dateTime('work_completed_at')->nullable();
            $table->dateTime('closed_at')->nullable();
            $table->integer('paused_seconds')->default(0);
            $table->string('sla_status', 30)->default('EN_PLAZO');
            $table->integer('row_version')->default(1);
            $table->timestamps();
            $table->foreignId('created_by')->nullable()->constrained('user')->nullOnDelete();
            $table->foreignId('updated_by')->nullable()->constrained('user')->nullOnDelete();

            $table->index(['area_id', 'status_id', 'assignee_id']);
            $table->index(['area_id', 'created_at']);
        });

        Schema::create('ticket_transition_log', function (Blueprint $table) {
            $table->id();
            $table->foreignId('ticket_id')->constrained('ticket')->cascadeOnDelete();
            $table->foreignId('from_status_id')->nullable()->constrained('ticket_status')->nullOnDelete();
            $table->foreignId('to_status_id')->constrained('ticket_status')->cascadeOnDelete();
            $table->foreignId('transition_id')->nullable()->constrained('workflow_transition')->nullOnDelete();
            $table->foreignId('user_id')->constrained('user')->cascadeOnDelete();
            $table->foreignId('acting_on_behalf_of_id')->nullable()->constrained('user')->nullOnDelete();
            $table->text('comment')->nullable();
            $table->boolean('is_override')->default(false);
            $table->timestamp('created_at')->useCurrent();
        });

        Schema::create('approval_rule', function (Blueprint $table) {
            $table->id();
            $table->foreignId('area_id')->constrained('area')->cascadeOnDelete();
            $table->decimal('amount_min', 14, 2)->default(0.00);
            $table->decimal('amount_max', 14, 2)->nullable();
            $table->integer('level')->default(1);
            $table->foreignId('approver_role_id')->nullable()->constrained('role')->nullOnDelete();
            $table->foreignId('approver_user_id')->nullable()->constrained('user')->nullOnDelete();
            $table->string('approver_resolution', 50)->default('ROL');
            $table->json('condition_expression')->nullable();
            $table->boolean('is_sequential')->default(true);
            $table->integer('sla_hours')->default(48);
            $table->integer('version')->default(1);
            $table->dateTime('valid_from')->nullable();
            $table->dateTime('valid_to')->nullable();
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });

        Schema::create('approval', function (Blueprint $table) {
            $table->id();
            $table->foreignId('ticket_id')->constrained('ticket')->cascadeOnDelete();
            $table->foreignId('rule_id')->constrained('approval_rule')->cascadeOnDelete();
            $table->integer('round')->default(1);
            $table->integer('level')->default(1);
            $table->foreignId('approver_id')->constrained('user')->cascadeOnDelete();
            $table->string('status', 30)->default('PENDIENTE');
            $table->text('decision_comment')->nullable();
            $table->decimal('amount_at_request', 14, 2);
            $table->timestamp('requested_at')->useCurrent();
            $table->dateTime('decided_at')->nullable();
            $table->foreignId('decided_by')->nullable()->constrained('user')->nullOnDelete();
            $table->foreignId('acting_on_behalf_of_id')->nullable()->constrained('user')->nullOnDelete();
            $table->dateTime('escalated_at')->nullable();
            $table->foreignId('escalated_to_id')->nullable()->constrained('user')->nullOnDelete();

            $table->unique(['ticket_id', 'round', 'level', 'approver_id']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('approval');
        Schema::dropIfExists('approval_rule');
        Schema::dropIfExists('ticket_transition_log');
        Schema::dropIfExists('ticket');
        Schema::dropIfExists('workflow_transition');
        Schema::dropIfExists('ticket_status');
    }
};
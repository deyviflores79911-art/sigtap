<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('notification', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained('user')->cascadeOnDelete();
            $table->foreignId('ticket_id')->nullable()->constrained('ticket')->nullOnDelete();
            $table->string('event_type', 100);
            $table->text('message');
            $table->string('link', 255)->nullable();
            $table->string('priority', 20)->default('MEDIA');
            $table->boolean('is_read')->default(false);
            $table->timestamp('created_at')->useCurrent();
            $table->timestamp('read_at')->nullable();
            $table->timestamp('expires_at')->nullable();
            $table->timestamp('email_sent_at')->nullable();
            $table->text('email_error')->nullable();
        });

        Schema::create('notification_preference', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained('user')->cascadeOnDelete();
            $table->string('event_type', 100);
            $table->boolean('in_app')->default(true);
            $table->boolean('email')->default(true);
            $table->timestamps();

            $table->unique(['user_id', 'event_type']);
        });

        Schema::create('activity_log', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->nullable()->constrained('user')->nullOnDelete();
            $table->string('action_type', 100);
            $table->string('entity_type', 100);
            $table->unsignedBigInteger('entity_id')->nullable();
            $table->foreignId('area_id')->nullable()->constrained('area')->nullOnDelete();
            $table->json('details')->nullable();
            $table->string('ip_address', 45)->nullable();
            $table->text('user_agent')->nullable();
            $table->string('correlation_id', 100)->nullable();
            $table->string('severity', 20)->default('INFO');
            $table->timestamp('created_at')->useCurrent();

            $table->index(['entity_type', 'entity_id', 'created_at']);
        });

        Schema::create('jobs', function (Blueprint $table) {
            $table->id();
            $table->string('queue')->index();
            $table->longText('payload');
            $table->unsignedTinyInteger('attempts');
            $table->unsignedInteger('reserved_at')->nullable();
            $table->unsignedInteger('available_at');
            $table->unsignedInteger('created_at');
        });

        Schema::create('failed_jobs', function (Blueprint $table) {
            $table->id();
            $table->string('uuid')->unique();
            $table->text('connection');
            $table->text('queue');
            $table->longText('payload');
            $table->longText('exception');
            $table->timestamp('failed_at')->useCurrent();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('failed_jobs');
        Schema::dropIfExists('jobs');
        Schema::dropIfExists('activity_log');
        Schema::dropIfExists('notification_preference');
        Schema::dropIfExists('notification');
    }
};
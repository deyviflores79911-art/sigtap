<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('user', function (Blueprint $table) {
            $table->id();
            $table->string('email', 150)->unique();
            $table->string('password_hash', 255);
            $table->string('full_name', 150);
            $table->string('phone', 50)->nullable();
            $table->string('avatar_path', 255)->nullable();
            $table->boolean('is_active')->default(true);
            $table->boolean('must_change_password')->default(true);
            $table->smallInteger('failed_attempts')->default(0);
            $table->dateTime('locked_until')->nullable();
            $table->dateTime('last_login_at')->nullable();
            $table->string('last_login_ip', 45)->nullable();
            $table->dateTime('password_changed_at')->nullable();
            $table->unsignedBigInteger('default_area_id')->nullable();
            $table->timestamps();
            $table->unsignedBigInteger('created_by')->nullable();
            $table->unsignedBigInteger('updated_by')->nullable();
        });

        Schema::create('password_history', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained('user')->cascadeOnDelete();
            $table->string('password_hash', 255);
            $table->timestamp('created_at')->useCurrent();
        });

        Schema::create('password_reset_token', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained('user')->cascadeOnDelete();
            $table->string('token_hash', 255)->unique();
            $table->dateTime('expires_at');
            $table->dateTime('used_at')->nullable();
            $table->string('requested_ip', 45)->nullable();
            $table->timestamp('created_at')->useCurrent();
        });

        Schema::create('session', function (Blueprint $table) {
            $table->string('id', 255)->primary();
            $table->foreignId('user_id')->nullable()->constrained('user')->nullOnDelete();
            $table->string('ip_address', 45)->nullable();
            $table->text('user_agent')->nullable();
            $table->longText('payload');
            $table->integer('last_activity')->index();
        });

        Schema::create('login_attempt', function (Blueprint $table) {
            $table->id();
            $table->string('email_attempted', 150);
            $table->foreignId('user_id')->nullable()->constrained('user')->nullOnDelete();
            $table->boolean('was_successful');
            $table->string('ip_address', 45)->nullable();
            $table->text('user_agent')->nullable();
            $table->timestamp('created_at')->useCurrent();
        });

        Schema::create('role', function (Blueprint $table) {
            $table->id();
            $table->string('code', 50)->unique();
            $table->string('name', 100);
            $table->text('description')->nullable();
            $table->boolean('is_global')->default(false);
            $table->timestamps();
        });

        Schema::create('area', function (Blueprint $table) {
            $table->id();
            $table->string('code', 20)->unique();
            $table->string('name', 100);
            $table->text('description')->nullable();
            $table->string('prefix_code', 10);
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });

        Schema::create('user_role', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained('user')->cascadeOnDelete();
            $table->foreignId('role_id')->constrained('role')->cascadeOnDelete();
            $table->foreignId('area_id')->nullable()->constrained('area')->cascadeOnDelete();
            $table->foreignId('assigned_by')->nullable()->constrained('user')->nullOnDelete();
            $table->timestamp('assigned_at')->useCurrent();
            $table->boolean('is_active')->default(true);

            $table->unique(['user_id', 'role_id', 'area_id']);
        });

        Schema::create('approval_delegation', function (Blueprint $table) {
            $table->id();
            $table->foreignId('delegator_id')->constrained('user')->cascadeOnDelete();
            $table->foreignId('delegate_id')->constrained('user')->cascadeOnDelete();
            $table->foreignId('area_id')->nullable()->constrained('area')->nullOnDelete();
            $table->dateTime('valid_from');
            $table->dateTime('valid_to');
            $table->text('reason')->nullable();
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });

        Schema::create('cost_center', function (Blueprint $table) {
            $table->id();
            $table->string('code', 50)->unique();
            $table->string('name', 150);
            $table->foreignId('manager_id')->nullable()->constrained('user')->nullOnDelete();
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('cost_center');
        Schema::dropIfExists('approval_delegation');
        Schema::dropIfExists('user_role');
        Schema::dropIfExists('area');
        Schema::dropIfExists('role');
        Schema::dropIfExists('login_attempt');
        Schema::dropIfExists('session');
        Schema::dropIfExists('password_reset_token');
        Schema::dropIfExists('password_history');
        Schema::dropIfExists('user');
    }
};
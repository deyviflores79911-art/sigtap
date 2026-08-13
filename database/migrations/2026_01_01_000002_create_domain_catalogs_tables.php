<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('location', function (Blueprint $table) {
            $table->id();
            $table->string('code', 50)->nullable();
            $table->string('name', 150);
            $table->foreignId('parent_id')->nullable()->constrained('location')->nullOnDelete();
            $table->string('address', 255)->nullable();
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });

        Schema::create('category', function (Blueprint $table) {
            $table->id();
            $table->foreignId('area_id')->constrained('area')->cascadeOnDelete();
            $table->foreignId('parent_id')->nullable()->constrained('category')->nullOnDelete();
            $table->string('name', 100);
            $table->string('code', 50);
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });

        Schema::create('priority', function (Blueprint $table) {
            $table->id();
            $table->string('code', 30)->unique();
            $table->string('name', 50);
            $table->string('color_hex', 10)->nullable();
            $table->integer('sla_response_hours')->default(24);
            $table->integer('sla_resolution_hours')->default(72);
            $table->integer('position')->default(0);
            $table->timestamps();
        });

        Schema::create('ticket_type', function (Blueprint $table) {
            $table->id();
            $table->foreignId('area_id')->constrained('area')->cascadeOnDelete();
            $table->string('code', 50);
            $table->string('name', 100);
            $table->text('description')->nullable();
            $table->boolean('requires_approval')->default(false);
            $table->boolean('requires_attachment')->default(false);
            $table->foreignId('default_priority_id')->nullable()->constrained('priority')->nullOnDelete();
            $table->integer('sla_hours_response')->nullable();
            $table->integer('sla_hours_resolution')->nullable();
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });

        Schema::create('ticket_type_field', function (Blueprint $table) {
            $table->id();
            $table->foreignId('ticket_type_id')->constrained('ticket_type')->cascadeOnDelete();
            $table->string('field_key', 50);
            $table->string('label', 100);
            $table->string('data_type', 30)->default('TEXT');
            $table->boolean('is_required')->default(false);
            $table->json('options')->nullable();
            $table->json('validation_rules')->nullable();
            $table->integer('position')->default(0);
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });

        Schema::create('asset', function (Blueprint $table) {
            $table->id();
            $table->string('code', 50)->unique();
            $table->string('name', 150);
            $table->foreignId('category_id')->nullable()->constrained('category')->nullOnDelete();
            $table->foreignId('location_id')->nullable()->constrained('location')->nullOnDelete();
            $table->string('brand', 100)->nullable();
            $table->string('model', 100)->nullable();
            $table->string('serial_number', 100)->nullable();
            $table->date('acquisition_date')->nullable();
            $table->string('criticality', 20)->default('MEDIA');
            $table->string('status', 30)->default('OPERATIVO');
            $table->foreignId('responsible_id')->nullable()->constrained('user')->nullOnDelete();
            $table->json('specs')->nullable();
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });

        Schema::create('vendor', function (Blueprint $table) {
            $table->id();
            $table->string('name', 150);
            $table->string('tax_id', 50)->nullable();
            $table->string('contact_name', 100)->nullable();
            $table->string('contact_number', 50)->nullable();
            $table->string('contact_email', 150)->nullable();
            $table->string('category', 100)->nullable();
            $table->decimal('rating_avg', 3, 2)->default(0.00);
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('vendor');
        Schema::dropIfExists('asset');
        Schema::dropIfExists('ticket_type_field');
        Schema::dropIfExists('ticket_type');
        Schema::dropIfExists('priority');
        Schema::dropIfExists('category');
        Schema::dropIfExists('location');
    }
};
<script setup lang="ts">
import { computed, reactive } from 'vue';
import { fetchRegister, fetchSendCaptcha } from '@/service/api/auth';
import { useAuthStore } from '@/store/modules/auth';
import { useRouterPush } from '@/hooks/common/router';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { useCaptcha } from '@/hooks/business/captcha';
import { $t } from '@/locales';

defineOptions({
  name: 'Register'
});

const { toggleLoginModule } = useRouterPush();
const { formRef, validate } = useNaiveForm();
const { label, isCounting, loading, start } = useCaptcha();
const authStore = useAuthStore();

interface FormModel {
  email: string;
  code: string;
  password: string;
  confirmPassword: string;
}

const model: FormModel = reactive({
  email: '',
  code: '',
  password: '',
  confirmPassword: ''
});

const rules = computed<Record<keyof FormModel, App.Global.FormRule[]>>(() => {
  const { formRules, createConfirmPwdRule } = useFormRules();

  return {
    email: formRules.email,
    code: formRules.code,
    password: formRules.pwd,
    confirmPassword: createConfirmPwdRule(model.password)
  };
});

async function handleSubmit() {
  await validate();
  const { error } = await fetchRegister(model);
  if (error) {
    window.$message?.error(error.message);
  } else {
    window.$message?.success($t('page.login.common.validateSuccess'));
    await authStore.login(model.email, model.password);
  }
}

async function handleSendCaptcha() {
  if (!model.email) {
    window.$message?.error($t('form.email.required'));
    return;
  }
  const { error } = await fetchSendCaptcha(model.email);
  if (error) {
    window.$message?.error(error.message);
  } else {
    window.$message?.success($t('page.login.codeLogin.sendCodeSuccess'));
    start();
  }
}
</script>

<template>
  <NForm ref="formRef" :model="model" :rules="rules" size="large" :show-label="false" @keyup.enter="handleSubmit">
    <NFormItem path="email">
      <NInput v-model:value="model.email" :placeholder="$t('page.login.common.emailPlaceholder')" />
    </NFormItem>
    <NFormItem path="code">
      <div class="w-full flex-y-center gap-16px">
        <NInput v-model:value="model.code" :placeholder="$t('page.login.common.codePlaceholder')" />
        <NButton size="large" :disabled="isCounting" :loading="loading" @click="handleSendCaptcha">
          {{ label }}
        </NButton>
      </div>
    </NFormItem>
    <NFormItem path="password">
      <NInput
        v-model:value="model.password"
        type="password"
        show-password-on="click"
        :placeholder="$t('page.login.common.passwordPlaceholder')"
      />
    </NFormItem>
    <NFormItem path="confirmPassword">
      <NInput
        v-model:value="model.confirmPassword"
        type="password"
        show-password-on="click"
        :placeholder="$t('page.login.common.confirmPasswordPlaceholder')"
      />
    </NFormItem>
    <NSpace vertical :size="18" class="w-full">
      <NButton type="primary" size="large" round block @click="handleSubmit">
        {{ $t('common.confirm') }}
      </NButton>
      <NButton size="large" round block @click="toggleLoginModule('pwd-login')">
        {{ $t('page.login.common.back') }}
      </NButton>
    </NSpace>
  </NForm>
</template>

<style scoped></style>
